"""Score the frozen paired-history trials using the original field definitions."""
from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

from evaluate_stability import metrics, parse_stability
from history_ablation import CONDITIONS, load_module, sha
from providers import parse_provider

FIELDS = ('stage', 'turn', 'blind', 'community', 'bet', 'my_chips', 'opp_chips', 'outcome')
LABELS = ('LS', 'TO', 'BI', 'CC', 'CB', 'RCI', 'OCI', 'SO')


def completed_response(raw: dict, stdout: str, manifest: dict) -> tuple[dict, int]:
    """Recognize a successful Codex completion after recoverable stream notices.

    Args:
        raw (dict): Unmodified saved provider record.
        stdout (str): Unmodified CLI event stream.
        manifest (dict): Exact provider/model configuration.

    Returns:
        tuple[dict, int]: Effective parsing record and recovered notice count.
        Only zero-exit, exactly-one-completion turns qualify. A failed turn,
        any other error, model mismatch, fallback or tool access still rejects.
        No model call or answer is repeated or selected by its correctness.
    """
    if manifest.get('harness', 'codex') != 'codex' or raw['returncode'] != 0:
        return raw, 0
    try:
        events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    except ValueError:
        return raw, 0
    if sum(e.get('type') == 'turn.completed' for e in events) != 1 or any(e.get('type') == 'turn.failed' for e in events):
        return raw, 0
    filtered, removed = [], 0
    for event in events:
        message = event.get('message', '')
        if (event.get('type') == 'error' and isinstance(message, str)
            and message.startswith('Reconnecting...') and 'stream disconnected before completion' in message):
            removed += 1
        else:
            filtered.append(event)
    if not removed:
        return raw, 0
    parsed = parse_provider('\n'.join(json.dumps(e) for e in filtered), 0, manifest['model'], 'codex')
    if parsed['status'] not in {'completed', 'invalid_json'}:
        return raw, 0
    return {**raw, **parsed}, removed


def answer_object(raw: dict, normalize_fence: bool = False) -> dict | None:
    """Read a validated answer, optionally removing exactly one outer code fence.

    Args:
        raw (dict): Provider-validated record; model/tool checks already passed
            before a response can have completed or invalid_json status.
        normalize_fence (bool): Enable the separately reported formatting diagnostic.

    Returns:
        dict | None: Unmodified JSON contents. Prose, multiple JSON objects,
        execution errors and model/tool mismatches are never repaired.
    """
    if raw['status'] == 'completed':
        return raw.get('prediction')
    if not normalize_fence or raw['status'] != 'invalid_json':
        return None
    answer = raw.get('result')
    if answer is None and raw.get('assistant_messages'):
        answer = raw['assistant_messages'][-1]
    if not isinstance(answer, str):
        return None
    match = re.fullmatch(r'\s*```(?:json)?\s*\n(.*?)\n```\s*', answer, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def fraction(values: list[bool]) -> dict:
    """Return denominator, correct count and accuracy for boolean values."""
    return {'n': len(values), 'correct': sum(values),
            'accuracy': sum(values)/len(values) if values else None}


def aggregate(records: list[dict]) -> dict:
    """Summarize field scores and direct stability from scored trial records.

    Args:
        records (list[dict]): Per-trial scores with explicit field eligibility.

    Returns:
        dict: Counts, field macro-average, original Overall and Overall+stability.
        Invalid predictions remain in every applicable denominator.
    """
    result = {'n': len(records), 'statuses': dict(Counter(r['status'] for r in records)),
              'overall': fraction([r['overall'] for r in records]),
              'overall_plus_stability': fraction([r['overall_plus_stability'] for r in records]),
              'fields': {c: fraction([r['fields'][c] for r in records if c in r['fields']]) for c in FIELDS},
              'stability': metrics([{'truth': r['stable_truth'], 'prediction': r['stable_prediction']} for r in records])}
    accuracies = [result['fields'][c]['accuracy'] for c in FIELDS]
    result['field_macro_average'] = sum(accuracies)/len(accuracies) if all(a is not None for a in accuracies) else None
    return result


def paired_summary(records: list[dict], seed: int = 20261110) -> dict:
    """Compute paired Overall differences, clustering repetitions by scene.

    Args:
        records (list[dict]): Both conditions with the same problem/repeat keys.
        seed (int): Fixed bootstrap seed, independent of outcomes.

    Returns:
        dict: Pair counts, per-scene mean differences and percentile 95% interval
        from 10,000 scene-level resamples. Difference is ablated minus annotated.
    """
    indexed = {(r['condition'], r['problem'], r['repeat']): r for r in records}
    scenes: dict[str, list[int]] = {}
    counts = Counter()
    for r in records:
        if r['condition'] != 'annotated':
            continue
        other = indexed[('images_only_history', r['problem'], r['repeat'])]
        a, b = r['overall'], other['overall']
        counts['both_correct' if a and b else 'annotated_only' if a else 'ablated_only' if b else 'both_wrong'] += 1
        scenes.setdefault(r['problem'], []).append(int(b)-int(a))
    differences = {key: sum(values)/len(values) for key, values in scenes.items()}
    values = list(differences.values())
    if not values:
        return {'pairs': 0}
    generator = random.Random(seed)
    boot = sorted(sum(generator.choices(values, k=len(values)))/len(values) for _ in range(10000))
    return {'pairs': sum(counts.values()), 'scene_count': len(scenes), 'pair_counts': dict(counts),
            'overall_difference': sum(values)/len(values),
            'scene_cluster_bootstrap_95_percentile': [boot[249], boot[9749]],
            'scene_mean_differences': differences, 'bootstrap_seed': seed, 'bootstrap_resamples': 10000}


def score(repo: Path, output: Path, normalize_fence: bool = False) -> dict:
    """Score a complete campaign and save auditable scene-level records.

    Args:
        repo (Path): Original evaluator, labels and problem-type definitions.
        output (Path): Frozen campaign containing every expected trial record.
        normalize_fence (bool): Write a separate outer-code-fence diagnostic;
            default strict scoring is retained in its own files.

    Returns:
        dict: Paired condition summaries, repeat scores and provenance.
        Missing trials raise an error rather than silently shrinking denominators.
    """
    ec = load_module(repo/'perception_eval/evaluate_column.py', 'original_columns')
    truth, types = ec.load_reference_data()
    manifest = json.loads((output/'manifest.json').read_text())
    eligibility = {c: set(ec.denominator_ids(c, types, truth, 'high')) for c in FIELDS}
    records = []
    for condition in CONDITIONS:
        for repeat in range(1, manifest['repeats']+1):
            for number in range(1, 37):
                pid = f'p{number}'
                path = output/'trials'/condition/f'repeat_{repeat}'/pid/'record.json'
                raw = json.loads(path.read_text())
                public = manifest['problems'][pid]
                if (raw['problem'], raw['condition'], raw['repeat'], raw['model']) != (pid, condition, repeat, manifest['model']):
                    raise ValueError(f'Trial identity mismatch: {path}')
                if raw['prompt_sha256'] != public['prompts'][condition]['sha256'] or raw['images_sha256'] != [p['sha256'] for p in public['images']]:
                    raise ValueError(f'Trial input mismatch: {path}')
                stdout = (path.parent/'stdout.jsonl').read_text()
                parsed = parse_provider(stdout, raw['returncode'],
                                        manifest['model'], manifest.get('harness', 'codex'), manifest.get('resolved_model'))
                if parsed['status'] != raw['status'] or parsed['prediction'] != raw['prediction']:
                    raise ValueError(f'Raw response mismatch: {path}')
                effective, recovered_notices = completed_response(raw, stdout, manifest)
                summary = answer_object(effective, normalize_fence)
                pred = ec.extract_prediction(summary) if isinstance(summary, dict) else None
                all_scores = {c: bool(ec.score_column(c, pred, truth[pid])[0]) if pred is not None else False
                              for c in FIELDS}
                overall = all(all_scores[c] for c in ec.relevant_columns(types[pid], truth[pid]))
                stable, stability_status = parse_stability(summary) if isinstance(summary, dict) else (None, raw['status'])
                stable_truth = truth[pid]['label']['table']['scene_stable']
                records.append({'problem': pid, 'condition': condition, 'repeat': repeat,
                                'has_history_images': len(manifest['problems'][pid]['images']) > 1,
                                'status': effective['status'], 'source_status': raw['status'],
                                'recovered_connection_notices': recovered_notices,
                                'fields': {c: all_scores[c] for c in FIELDS if pid in eligibility[c]},
                                'fence_removed': normalize_fence and effective['status'] == 'invalid_json' and summary is not None,
                                'overall': overall, 'overall_plus_stability': overall and stable is stable_truth,
                                'stable_truth': stable_truth, 'stable_prediction': stable,
                                'stability_status': stability_status, 'source_sha256': sha(path)})
    report = {'model': manifest['model'], 'harness': manifest.get('harness', 'codex'),
              'scoring': 'single_outer_code_fence_removed' if normalize_fence else 'strict_json',
              'fence_removed_count': sum(r['fence_removed'] for r in records),
              'successful_turns_with_recovered_connection_notices': sum(r['recovered_connection_notices'] > 0 for r in records),
              'resolved_model': manifest.get('resolved_model'), 'conditions': {},
              'provenance': {'manifest_sha256': sha(output/'manifest.json'), 'scorer_sha256': sha(Path(__file__)),
                             'original_evaluator_sha256': sha(repo/'perception_eval/evaluate_column.py'),
                             'ground_truth_sha256': sha(ec.GROUND_TRUTH), 'problem_types_sha256': sha(ec.PROBLEM_TYPES)},
              'paired_all_scenes': paired_summary(records),
              'paired_history_scenes': paired_summary([r for r in records if r['has_history_images']])}
    for condition in CONDITIONS:
        selected = [r for r in records if r['condition'] == condition]
        report['conditions'][condition] = {
            **aggregate(selected),
            'repeats': [{'repeat': repeat, **aggregate([r for r in selected if r['repeat'] == repeat])}
                        for repeat in range(1, manifest['repeats']+1)],
            'history_scenes': aggregate([r for r in selected if r['has_history_images']]),
            'no_history_scenes': aggregate([r for r in selected if not r['has_history_images']])}
    suffix = '_fence_normalized' if normalize_fence else ''
    (output/f'summary{suffix}.json').write_text(json.dumps(report, indent=2)+'\n')
    (output/f'scores{suffix}.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    lines = [f"# Paired annotated-history ablation — {manifest['model']}, 2026-11-10", '',
             'Fresh matched tool-free runs: 36 scenes × 3 trial repetitions × 2 conditions. '
             'Both conditions receive every historical image through the current frame, the same native '
             'field guidelines, and the same structured-output task. The ablated condition removes all '
             'prior parsed states, action_sequence.json (including prior LS), and hole_card_cache.json '
             '(including blind cache). This tests removal of all annotated prior context, not just parsed states.', '',
             'The direct-image harness differs from the historical native-agent harness. Compare the two '
             'fresh conditions with each other; do not subtract their scores from the published table. '
             f"All trials use requested model {manifest['model']}, {manifest.get('harness', 'codex')} CLI, "
             f"effort: {manifest['effort']}; service tier: {manifest['service_tier']}. "
             'Tools are disabled and each trial starts a fresh session. No score-based retries. '
             'No-answer service failures may be retried with the earlier attempt preserved under attempts/. '
             'Quota-recovery events, if any, are recorded separately.', '',
             '| Condition | Overall | Field average | LS | TO | BI | CC | CB | RCI | OCI | SO | Stability | Stable recall | Unstable recall | Balanced stability | Overall + stability |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for condition, result in report['conditions'].items():
        stable = result['stability']
        scores = [result['overall']['accuracy'], result['field_macro_average']]
        scores += [result['fields'][c]['accuracy'] for c in FIELDS]
        scores += [stable['accuracy'], stable['stable']['recall'], stable['unstable']['recall'],
                   stable['balanced_accuracy'], result['overall_plus_stability']['accuracy']]
        lines.append('| '+condition+' | '+' | '.join(f'{v*100:.1f}%' for v in scores)+' |')
    lines += ['', 'Field denominators per repeat: '+', '.join(f'{label} {len(eligibility[c])}' for label, c in zip(LABELS, FIELDS))+'. '
              'Field average is the unweighted mean of the eight field accuracies. Original Overall uses '
              'the original per-problem relevant-column conjunction; stability is added only in the separate extended score.', '',
              '| Condition | Repeat Overall /36 | Repeat stability /36 | History scenes Overall | No-history scenes Overall | Status counts |',
              '|---|---|---|---|---|---|']
    for condition, result in report['conditions'].items():
        hist, nohist = result['history_scenes']['overall'], result['no_history_scenes']['overall']
        lines.append(f"| {condition} | {', '.join(str(r['overall']['correct']) for r in result['repeats'])} | "
                     f"{', '.join(str(r['stability']['correct']) for r in result['repeats'])} | "
                     f"{hist['correct']}/{hist['n']} | {nohist['correct']}/{nohist['n']} | {result['statuses']} |")
    for key, label in [('paired_all_scenes', 'All scenes'), ('paired_history_scenes', 'Scenes with image history')]:
        paired = report[key]
        low, high = paired['scene_cluster_bootstrap_95_percentile']
        lines += ['', f"{label}: ablated minus annotated Overall = {100*paired['overall_difference']:.1f} percentage points; "
                  f"descriptive paired scene-cluster bootstrap 95% interval [{100*low:.1f}, {100*high:.1f}] pp. "
                  f"Pair counts: {paired['pair_counts']}. Repeated attempts are clustered by scene, not treated as independent scenes."]
    lines += ['', 'Stability labels: 31 stable / 5 unstable. Always-stable baseline: 86.1% accuracy, '
              '0% unstable recall, 50% balanced accuracy. Missing or invalid responses remain errors in all applicable denominators.', '',
              'This small diagnostic does not establish a model ranking. It does not add held-card identity to the '
              '36-scene score; the separate 11-image held-card diagnostic remains a distinct experiment.', '',
              f"Scoring mode: {report['scoring']}. Outer code fences removed in {report['fence_removed_count']} responses. "
              'The formatting diagnostic accepts only a single fenced JSON object with no surrounding prose; '
              'it never selects between multiple answers, changes field values, or repairs malformed JSON. '
              'Provider/model/tool validity checks remain identical.', '',
              f"Successful zero-exit Codex turns with recovered connection notices: {report['successful_turns_with_recovered_connection_notices']}. "
              'A transient reconnect notice does not invalidate a later completed answer; failed turns '
              'or non-transport errors remain invalid. Original events and parsing statuses are retained.', '',
              f'Audit artifacts: [manifest](manifest.json), [summary](summary{suffix}.json), [scene-level scores](scores{suffix}.jsonl), '
              'frozen prompts under inputs/, and unmodified CLI events plus parsed records under trials/.', '']
    if manifest.get('resolved_model'):
        lines += [f"Requested ID {manifest['model']} was served as {manifest['resolved_model']}; "
                  'this is not evidence for the retired preview snapshot.', '']
    elif manifest.get('harness', 'codex') == 'codex':
        lines += ['Model identity evidence is the requested CLI ID; Codex JSONL does not attest the backend ID.', '']
    (output/f'README{suffix}.md').write_text('\n'.join(lines))
    return report


def main() -> None:
    """Score a completed paired campaign; incomplete campaigns fail explicitly."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--normalize-fences', action='store_true')
    args = parser.parse_args()
    result = score(args.repo.resolve(), args.output.resolve(), args.normalize_fences)
    print(json.dumps({key: {'overall': row['overall'], 'stability': row['stability']}
                      for key, row in result['conditions'].items()}, indent=2))


if __name__ == '__main__':
    main()
