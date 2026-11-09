"""Derive an honestly named stable Flash-Lite result from immutable legacy-ID requests."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path

from run_claude import sha256
from run_gemini import parse_response

LEGACY = 'gemini-3.1-flash-lite-preview'
STABLE = 'gemini-3.1-flash-lite'


def resolve_record(record: dict, stdout: str) -> dict:
    """Revalidate a response under its verified, explicitly reported model identity.

    Args:
        record (dict): Original campaign record, never modified in place.
        stdout (str): Original CLI JSON response, including model usage.

    Returns:
        dict: Derived record retaining the requested ID and original validation status.

    Raises:
        ValueError: The known retired alias did not resolve solely to the stable ID.
    """
    requested = record['model']
    actual = STABLE if requested == LEGACY else requested
    if record['resolved_models'] != [actual]:
        raise ValueError('Unexpected model substitution; refusing to adopt result')
    parsed = parse_response(stdout, record['returncode'], actual)
    return {**record, **parsed, 'model': actual, 'requested_model': requested,
            'original_validation_status': record['status']}


def derive(root: Path, source: Path, output: Path) -> None:
    """Create a separate derived campaign, preserving every original request and response.

    Args:
        root (Path): Frozen dataset package used by the source campaign.
        source (Path): Completed raw legacy-request campaign.
        output (Path): New directory; existing paths are rejected.
    """
    manifest = json.loads((source / 'manifest.json').read_text())
    records = [json.loads(p.read_text()) for p in sorted(source.glob('*/repeat_*/*/record.json'))]
    expected = {(m, r, i) for m in manifest['models'].values()
                for r in range(1, manifest['repeats']+1) for i in manifest['image_sha256']}
    actual = {(r['model'], r['repeat'], r['id']) for r in records}
    if len(records) != len(expected) or actual != expected:
        raise ValueError('Source campaign is incomplete')
    if sha256(root / 'private/labels.json') != manifest['labels_sha256']:
        raise ValueError('Labels changed since inference')
    if sha256(root / 'score.py') != manifest['scorer_sha256']:
        raise ValueError('Scorer changed since inference')
    output.mkdir(parents=True, exist_ok=False)
    manifest['models'] = {'Gemini 3 Flash': 'gemini-3-flash-preview',
                          'Gemini 3.1 Flash Lite (stable)': STABLE}
    manifest['model_resolution'] = {
        'requested': LEGACY, 'reported_actual': STABLE,
        'note': 'Current stable model, not a reproduction of the retired paper preview.',
        'source': 'https://ai.google.dev/gemini-api/docs/deprecations',
    }
    manifest['source_manifest_sha256'] = sha256(source / 'manifest.json')
    manifest['resolution_script_sha256'] = sha256(Path(__file__))
    manifest['validation_tests'] = 13
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    shutil.copyfile(source / 'gemini_version.txt', output / 'gemini_version.txt')
    for original in records:
        src = source / original['model'] / f"repeat_{original['repeat']}" / original['id']
        record = resolve_record(original, (src / 'stdout.json').read_text())
        record['source_record_sha256'] = sha256(src / 'record.json')
        dst = output / record['model'] / f"repeat_{record['repeat']}" / record['id']
        dst.mkdir(parents=True)
        for name in ('stdout.json', 'stderr.txt'):
            shutil.copyfile(src / name, dst / name)
        (dst / 'record.json').write_text(json.dumps(record, indent=2)+'\n')
    spec = importlib.util.spec_from_file_location('held_card_score', root / 'score.py')
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    gold = json.loads((root / 'private/labels.json').read_text())
    subsets = json.loads((root / 'private/subsets.json').read_text())
    report = {'label_status': gold['label_status'], 'models': []}
    for name, model in manifest['models'].items():
        row = {'name': name, 'model': model, 'repeats': []}
        for repeat in range(1, manifest['repeats']+1):
            directory = output / model / f'repeat_{repeat}'
            items = [json.loads(p.read_text()) for p in sorted(directory.glob('*/record.json'))]
            predictions = [{'id': r['id'], 'held_card': r['held_card']} for r in items
                           if r['status'] in {'completed', 'invalid_answer'}]
            metrics = {'repeat': repeat, 'finished': len(items),
                       'execution_errors': sum(r['status'] not in {'completed', 'invalid_answer'} for r in items)}
            for subset, ids in subsets.items():
                metrics[subset] = scorer.score([g for g in gold['items'] if g['id'] in ids],
                                              [p for p in predictions if p['id'] in ids])
            (directory / 'predictions.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in predictions))
            (directory / 'scores.json').write_text(json.dumps(metrics, indent=2)+'\n')
            row['repeats'].append(metrics)
        report['models'].append(row)
    (output / 'summary.json').write_text(json.dumps(report, indent=2)+'\n')


def main() -> None:
    """Resolve the documented alias offline; no model calls are made."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset', type=Path)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    derive(args.dataset, args.source, args.output)


if __name__ == '__main__':
    main()
