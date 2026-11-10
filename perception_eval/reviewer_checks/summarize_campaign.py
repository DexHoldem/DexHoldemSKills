"""Summarize complete paired campaigns without dropping missing model trials."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from history_ablation import sha
from providers import MODELS
from score_history import score

DISPLAY = {'gpt-6-astra': 'GPT 6 Astra', 'gpt-6-sol': 'GPT 6 Sol',
           'gpt-5.6-sol': 'GPT 5.6 Sol', 'gpt-5.6-luna': 'GPT 5.6 Luna',
           'gpt-5.5': 'GPT 5.5', 'gpt-5.4': 'GPT 5.4', 'gpt-5.4-mini': 'GPT 5.4 mini',
           'claude-opus-5-5': 'Claude Opus 5.5', 'claude-sonnet-5': 'Claude Sonnet 5',
           'claude-opus-4-7': 'Claude Opus 4.7', 'claude-sonnet-4-6': 'Claude Sonnet 4.6',
           'claude-haiku-4-5': 'Claude Haiku 4.5', 'gemini-3-flash-preview': 'Gemini 3 Flash',
           'gemini-3.1-flash-lite-preview': 'Gemini 3.1 Flash Lite (served stable)'}


def summarize(repo: Path, astra: Path, campaign: Path, destination: Path,
              require_complete: bool = True) -> dict:
    """Collect each model's paired results only when all 216 planned records exist.

    Args:
        repo (Path): Source evaluator and labels.
        astra (Path): Original completed Astra campaign, reused without new inference.
        campaign (Path): Multi-provider probes and model directories.
        destination (Path): Consolidated report directory.
        require_complete (bool): Refuse a final report while an available model is incomplete.

    Returns:
        dict: Coverage and both strict and fence-normalized paired results.
        Unavailable models remain explicitly unavailable, never scored as zero.
    """
    baseline = json.loads((astra/'manifest.json').read_text())
    rows = []
    for model, harness in MODELS.items():
        directory = astra if model == 'gpt-6-astra' else campaign/'models'/model
        availability_path = campaign/'probes'/model/'availability.json'
        availability = json.loads(availability_path.read_text()) if availability_path.exists() else None
        row = {'model': model, 'name': DISPLAY[model], 'harness': harness, 'availability': availability}
        if availability is not None and not availability['available']:
            row.update(status='unavailable', finished_trials=0)
            rows.append(row)
            continue
        paths = sorted((directory/'trials').glob('*/*/*/record.json'))
        row['finished_trials'] = sum('returncode' in json.loads(p.read_text()) for p in paths)
        if row['finished_trials'] != 216:
            row['status'] = 'incomplete'
            rows.append(row)
            continue
        manifest = json.loads((directory/'manifest.json').read_text())
        if manifest['problems'] != baseline['problems']:
            raise ValueError(f'Cross-model input mismatch: {model}')
        row['status'] = 'complete'
        row['manifest_sha256'] = sha(directory/'manifest.json')
        # Recompute from frozen raw responses, never trust an old aggregate blindly.
        row['strict'] = score(repo, directory)
        row['fence_normalized'] = score(repo, directory, normalize_fence=True)
        row['preserved_failed_attempts'] = len(list((directory/'attempts').glob('*/*/*/*/record.json')))
        rows.append(row)
    incomplete = [r['model'] for r in rows if r['status'] == 'incomplete']
    if require_complete and incomplete:
        raise ValueError('Unfinished models: '+', '.join(incomplete))
    report = {'protocol': 'paired_history_ablation_v1', 'scenes': 36, 'repeats': 3,
              'planned_models': 14, 'completed_models': sum(r['status'] == 'complete' for r in rows),
              'unavailable_models': [r['model'] for r in rows if r['status'] == 'unavailable'],
              'incomplete_models': incomplete, 'models': rows,
              'same_images_and_prompts_verified': True,
              'scorer_sha256': sha(Path(__file__).with_name('score_history.py'))}
    destination.mkdir(parents=True, exist_ok=True)
    (destination/'campaign_summary.json').write_text(json.dumps(report, indent=2)+'\n')
    lines = ['# All-paper-model paired annotation ablation — 2026-11-10', '',
             f"Coverage: {report['completed_models']} complete model configurations; "
             f"{len(report['unavailable_models'])} unavailable; {len(incomplete)} incomplete. "
             'Each complete configuration has 36 scenes × 3 repetitions × 2 conditions. '
             'Model access/long-input probes are excluded from scoring.', '',
             '**A** supplies all historical/current images and prior annotations/caches. '
             '**B** supplies the identical historical/current images, removing prior parsed states, '
             'workflow-state cache and hole-card/blind cache. Neither arm drops historical images. '
             'The 24 scenes with history and 12 single-image scenes are also scored separately.', '',
             'This fresh tool-free harness differs from the old native-agent harness. Compare A vs B '
             'within each row; do not subtract from the paper table or infer a model ranking. '
             'Provider interfaces and reasoning budgets are not identical across families.', '',
             '## Strict JSON contract', '',
             '| Model | Valid JSON A/B /108 | Overall A | Overall B | Eight-field average A | Eight-field average B | Stability A | Stability B |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        if row['status'] != 'complete':
            lines.append(f"| {row['name']} | {row['status']} | — | — | — | — | — | — |")
            continue
        a, b = (row['strict']['conditions'][c] for c in ('annotated', 'images_only_history'))
        values = [a['overall']['accuracy'], b['overall']['accuracy'], a['field_macro_average'],
                  b['field_macro_average'], a['stability']['accuracy'], b['stability']['accuracy']]
        lines.append(f"| {row['name']} | {a['statuses'].get('completed',0)}/{b['statuses'].get('completed',0)} | "
                     +' | '.join(f'{v*100:.1f}%' for v in values)+' |')
    lines += ['', '## Single-code-fence formatting diagnostic', '',
              'This separate deterministic pass removes exactly one outer Markdown code fence '
              'around a JSON object. It does not change values, accept surrounding prose, select '
              'among multiple JSON objects, or repair malformed JSON. The same rule applies to every '
              'model and both conditions. Strict scores above and all original responses are retained.', '',
              '| Model | Fences removed /216 | Overall A | Overall B | B−A (pp) | Scene-paired 95% interval (pp) | Stability A/B | Balanced stability A/B | Unstable recall A/B |',
              '|---|---:|---:|---:|---:|---|---|---|---|']
    for row in rows:
        if row['status'] != 'complete':
            lines.append(f"| {row['name']} | {row['status']} | — | — | — | — | — | — | — |")
            continue
        result = row['fence_normalized']
        a, b = (result['conditions'][c] for c in ('annotated', 'images_only_history'))
        paired = result['paired_all_scenes']
        low, high = paired['scene_cluster_bootstrap_95_percentile']
        sa, sb = a['stability'], b['stability']
        lines.append(f"| {row['name']} | {result['fence_removed_count']} | {100*a['overall']['accuracy']:.1f}% | "
                     f"{100*b['overall']['accuracy']:.1f}% | {100*paired['overall_difference']:.1f} | "
                     f"[{100*low:.1f}, {100*high:.1f}] | {100*sa['accuracy']:.1f}% / {100*sb['accuracy']:.1f}% | "
                     f"{100*sa['balanced_accuracy']:.1f}% / {100*sb['balanced_accuracy']:.1f}% | "
                     f"{sa['unstable']['correct']}/15 / {sb['unstable']['correct']}/15 |")
    lines += ['', 'Stability gold labels comprise 31 stable and 5 unstable scenes. Always-stable baseline: '
              '86.1% accuracy, 0% unstable recall, 50% balanced accuracy. Confidence intervals resample '
              '36 scenes with their three repetitions together (10,000 resamples); 108 attempts are not '
              '108 independent scenes. These intervals are descriptive, with no multiplicity adjustment.', '',
              'GPT 5.5, GPT 5.4 and GPT 5.4 mini were rechecked after the plan upgrade and rejected by '
              'the current Codex ChatGPT-account route. The user authorized skipping these unavailable '
              'models. Gemini 3.1 Flash Lite preview resolves to `gemini-3.1-flash-lite`; usage metadata '
              'verifies the stable model, not the retired preview snapshot. Codex JSONL records the '
              'requested model ID but does not attest the backend ID.', '',
              'Astra preserves 20 pre-upgrade no-answer usage-limit failures under attempts/; these '
              'were retried after the user upgraded the plan. Other transient no-answer service errors '
              'may receive one preserved retry. Invalid or incorrect answers are never rerun by score. '
              'Probes, failure evidence, prompts, source image hashes, settings and raw responses remain available.', '',
              'The original scene-stability retrospective covers 10 model configurations separately. '
              'The 11-image held-card diagnostic is also separate and is not folded into this 36-scene aggregate.', '',
              '[Machine-readable full results](campaign_summary.json) include all fields, repeats, '
              'history strata, stricter Overall+stability, paired scene differences, and manifest hashes.', '']
    (destination/'README.md').write_text('\n'.join(lines))
    return report


def main() -> None:
    """Write a final complete report, or an explicitly partial report on request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--astra', type=Path, required=True)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-partial', action='store_true')
    args = parser.parse_args()
    report = summarize(args.repo.resolve(), args.astra.resolve(), args.campaign.resolve(),
                       args.output.resolve(), require_complete=not args.allow_partial)
    print(json.dumps({key: report[key] for key in ['completed_models','unavailable_models','incomplete_models']}, indent=2))


if __name__ == '__main__':
    main()
