"""Rescore scene stability from the exact saved runs behind the perception table."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


def digest(path: Path) -> str | None:
    """Return SHA-256 for path (Path), or None if the artifact is absent."""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def parse_stability(summary: dict[str, Any]) -> tuple[bool | None, str]:
    """Read explicit stability only, never infer it from loop stage.

    Args:
        summary (dict[str, Any]): Saved structured prediction. Canonical nested
            table.scene_stable and the legacy root scene_stable are supported.

    Returns:
        tuple[bool | None, str]: Boolean prediction and validation status.
            Conflicting, missing or malformed values remain incorrect.
    """
    candidates = []
    table = summary.get('table')
    if isinstance(table, dict) and 'scene_stable' in table:
        candidates.append(table['scene_stable'])
    if 'scene_stable' in summary:
        candidates.append(summary['scene_stable'])
    if not candidates:
        return None, 'missing_field'
    normalized = []
    for value in candidates:
        if isinstance(value, bool):
            normalized.append(value)
        elif isinstance(value, str) and value.strip().lower() in {'true', 'false'}:
            normalized.append(value.strip().lower() == 'true')
        else:
            return None, 'invalid_field'
    if len(set(normalized)) != 1:
        return None, 'conflicting_fields'
    return normalized[0], 'valid'


def metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute exact and class-balanced scores from records (list[dict]).

    Each record has a boolean truth and a bool-or-None prediction. Missing
    predictions remain in the denominators. The two class recalls are averaged
    only when both classes occur. Returns a dict of counts and rates.
    """
    output = {'n': len(records), 'correct': sum(r['prediction'] is r['truth'] for r in records),
              'missing_or_invalid': sum(r['prediction'] is None for r in records)}
    output['accuracy'] = output['correct']/output['n'] if records else None
    for name, truth in [('stable', True), ('unstable', False)]:
        subset = [r for r in records if r['truth'] is truth]
        correct = sum(r['prediction'] is truth for r in subset)
        output[name] = {'n': len(subset), 'correct': correct,
                        'recall': correct/len(subset) if subset else None}
    recalls = [output[name]['recall'] for name in ('stable', 'unstable')]
    output['balanced_accuracy'] = sum(recalls)/2 if all(r is not None for r in recalls) else None
    output['false_stable'] = sum(r['truth'] is False and r['prediction'] is True for r in records)
    output['false_unstable'] = sum(r['truth'] is True and r['prediction'] is False for r in records)
    return output


def evaluate(repo: Path, config: Path, destination: Path) -> dict:
    """Evaluate explicitly selected paper batches without modifying saved runs.

    Args:
        repo (Path): DexHoldem evaluation source with reference data and runs.
        config (Path): Model rows with exact ordered batch IDs (one per repeat).
        destination (Path): Output directory for summaries, records and manifest.

    Returns:
        dict: Per-model and per-repeat stability, original Overall and extended
            Overall requiring stability in addition to every original field.
    """
    spec = importlib.util.spec_from_file_location('original_evaluator', repo/'perception_eval/evaluate_column.py')
    ec = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ec)
    ground_truth, types = ec.load_reference_data()
    ids = sorted(ground_truth, key=ec.problem_sort_key)
    if len(ids) != 36 or any(not isinstance(ground_truth[p]['label']['table'].get('scene_stable'), bool) for p in ids):
        raise ValueError('Expected 36 problems with explicit boolean stability labels')
    configuration = json.loads(config.read_text())
    all_records, models = [], []
    sources = {str(p.relative_to(repo)): digest(p) for p in [ec.GROUND_TRUTH, ec.PROBLEM_TYPES,
                                                          repo/'perception_eval/evaluate_column.py']}
    for row in configuration['rows']:
        model_records, repeats = [], []
        for repeat, batch_name in enumerate(row['batches'], 1):
            batch_dir = Path(batch_name)
            if not batch_dir.is_absolute():
                batch_dir = repo/'perception_eval/batch_runs'/batch_name
            batch = ec.load_batch(batch_dir)
            for name in ['manifest.json', 'summary.json']:
                path = batch_dir/name
                if path.exists():
                    sources[str(path)] = digest(path)
            records = []
            for problem in ids:
                run_id = ec.run_id_for_problem(batch, problem)
                folder = repo/'bench/problems'/problem/'runs'/run_id
                valid, error, path = ec.run_output_status(folder, 'visual_summary.json')
                prediction, status = None, error or 'invalid_output'
                if valid:
                    try:
                        data = json.loads(path.read_text())
                        if not isinstance(data, dict):
                            raise ValueError('Summary is not an object')
                        prediction, status = parse_stability(data)
                    except (ValueError, OSError) as exc:
                        status = f'invalid_summary: {exc}'
                original = ec.score_run_columns(problem_id=problem, run_id=run_id, run_dir=folder,
                    columns=['overall'], summary_name='visual_summary.json',
                    problem_types=types, ground_truth=ground_truth)[0]['ok']
                truth = ground_truth[problem]['label']['table']['scene_stable']
                records.append({'model': row['perceiver'], 'harness': row['harness'], 'repeat': repeat,
                    'problem': problem, 'run_id': run_id, 'truth': truth, 'prediction': prediction,
                    'status': status, 'original_overall': original,
                    'extended_overall': original and prediction is truth,
                    'source': str(path.relative_to(repo)), 'summary_sha256': digest(path),
                    'output_check_sha256': digest(folder/'output_check.json')})
            repeats.append({'repeat': repeat, 'batch': batch_name, **metrics(records),
                            'original_overall': sum(r['original_overall'] for r in records),
                            'extended_overall': sum(r['extended_overall'] for r in records)})
            model_records.extend(records)
        aggregate = metrics(model_records)
        models.append({'model': row['perceiver'], 'harness': row['harness'], **aggregate,
                       'original_overall': sum(r['original_overall'] for r in model_records),
                       'extended_overall': sum(r['extended_overall'] for r in model_records), 'repeats': repeats})
        all_records.extend(model_records)
    baseline = metrics([{'truth': ground_truth[p]['label']['table']['scene_stable'], 'prediction': True} for p in ids])
    report = {'protocol': 'Offline rescore of original annotated-history runs; no new inference',
              'baseline_always_stable': baseline, 'models': models}
    destination.mkdir(parents=True, exist_ok=True)
    (destination/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    (destination/'records.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in all_records))
    (destination/'manifest.json').write_text(json.dumps({'config': configuration,
        'config_sha256': digest(config), 'scorer_sha256': digest(Path(__file__)),
        'sources_sha256': sources, 'label_counts': {k: baseline[k]['n'] for k in ['stable','unstable']},
        'normalization': 'Explicit nested/root boolean or true/false string only; conflicting aliases invalid',
        'invalid_policy': 'Same output_check gate as original paper; missing/invalid predictions count wrong'}, indent=2)+'\n')
    lines = ['# Scene-stability rescoring of original perception runs — 2026-11-10', '',
        'Same annotated-history outputs as the selected paper batches. No new inference. '
        'Each model has three repeats of 36 scenes, not 108 independent scenes.', '',
        'Gold: 31 stable and 5 unstable scenes. Always-stable baseline: 31/36 (86.1%) '
        'overall, 0/5 unstable recall, and 50.0% balanced accuracy.', '',
        '| Model | Per-repeat correct /36 | Stable /93 | Unstable /15 | Accuracy | Balanced accuracy | Missing/invalid | Original Overall /108 | Overall + stability /108 |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for row in models:
        lines.append(f"| {row['model']} | {', '.join(str(r['correct']) for r in row['repeats'])} | "
            f"{row['stable']['correct']} | {row['unstable']['correct']} | {row['accuracy']*100:.1f}% | "
            f"{row['balanced_accuracy']*100:.1f}% | {row['missing_or_invalid']} | "
            f"{row['original_overall']} | {row['extended_overall']} |")
    lines += ['', 'Stability is scored directly from saved scene_stable fields, never inferred from LS. '
        'Original Overall remains unchanged; the additional column is a separate, stricter diagnostic. '
        'No held-card field is added to this aggregate. Missing and invalid outputs remain in denominators.', '',
        'Per-problem predictions and source hashes: [records.jsonl](records.jsonl). '
        'Per-repeat scores and confusion counts: [summary.json](summary.json). '
        'Exact batch selection and provenance: [manifest.json](manifest.json).', '']
    (destination/'README.md').write_text('\n'.join(lines))
    return report


def main() -> None:
    """Rescore the explicit batch selection and print aggregate counts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(args.repo.resolve(), args.config.resolve(), args.output.resolve())
    for row in report['models']:
        print(row['model'], row['correct'], '/', row['n'], 'stable',row['stable'], 'unstable',row['unstable'])


if __name__ == '__main__':
    main()
