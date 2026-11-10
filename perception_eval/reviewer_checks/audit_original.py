"""Recompute original stability and Overall from the portable raw-output archive."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from evaluate_stability import metrics, parse_stability
from history_ablation import load_module, sha


def text_sha(text: str | None) -> str | None:
    """Return the UTF-8 hash of archived text (str), or None for missing files."""
    return hashlib.sha256(text.encode()).hexdigest() if text is not None else None


def audit(repo: Path, results: Path) -> dict:
    """Verify portable source artifacts and independently rederive saved scores.

    Args:
        repo (Path): Checkout containing the original scoring rules and labels.
        results (Path): Retrospective table plus source_outputs.jsonl archive.

    Returns:
        dict: Verified trial/model counts. Source hashes, field predictions,
        Overall and extended Overall must all match; mismatch raises ValueError.
        Does not require the original ignored batch/run directories.
    """
    ec = load_module(repo/'perception_eval/evaluate_column.py', 'original_audit_rules')
    truth, types = ec.load_reference_data()
    manifest = json.loads((results/'manifest.json').read_text())
    for relative in ('perception_eval/evaluate_column.py', 'bench/problems/ground_truth.json', 'bench/problems/problem_types.json'):
        if sha(repo/relative) != manifest['sources_sha256'][relative]:
            raise ValueError(f'Original reference changed: {relative}')
    records = [json.loads(line) for line in (results/'records.jsonl').read_text().splitlines()]
    sources = [json.loads(line) for line in (results/'source_outputs.jsonl').read_text().splitlines()]
    if len(records) != len(sources):
        raise ValueError('Archive count mismatch')
    for record, source in zip(records, sources):
        if any(record[k] != source[k] for k in ('model', 'repeat', 'problem', 'run_id')):
            raise ValueError('Archive identity mismatch')
        for key, raw_key in [('summary_sha256', 'visual_summary_text'), ('output_check_sha256', 'output_check_text')]:
            if record[key] != source[key] or source[key] != text_sha(source[raw_key]):
                raise ValueError('Archive hash mismatch')
        try:
            valid = bool(json.loads(source['output_check_text'] or '{}').get('ok'))
            summary = json.loads(source['visual_summary_text'] or 'null')
        except (ValueError, AttributeError):
            valid, summary = False, None
        valid = valid and isinstance(summary, dict)
        stable = parse_stability(summary)[0] if valid else None
        pred = ec.extract_prediction(summary) if valid else None
        pid = record['problem']
        overall = pred is not None and all(ec.score_column(c, pred, truth[pid])[0]
                                           for c in ec.relevant_columns(types[pid], truth[pid]))
        expected_stable = truth[pid]['label']['table']['scene_stable']
        if (stable is not record['prediction'] or expected_stable is not record['truth']
            or overall != record['original_overall']
            or (overall and stable is expected_stable) != record['extended_overall']):
            raise ValueError(f'Score mismatch: {record["run_id"]}')
    report = json.loads((results/'summary.json').read_text())
    for row in report['models']:
        selected = [r for r in records if r['model'] == row['model']]
        recomputed = metrics(selected)
        if any(row[key] != value for key, value in recomputed.items()):
            raise ValueError(f'Aggregate mismatch: {row["model"]}')
        if row['original_overall'] != sum(r['original_overall'] for r in selected):
            raise ValueError('Overall count mismatch')
        if row['extended_overall'] != sum(r['extended_overall'] for r in selected):
            raise ValueError('Extended Overall count mismatch')
    return {'verified_trials': len(records), 'verified_models': len(report['models'])}


def main() -> None:
    """Audit the portable archive without using original run directories."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.repo.resolve(), args.results.resolve()), indent=2))


if __name__ == '__main__':
    main()
