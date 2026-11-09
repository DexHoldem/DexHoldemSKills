"""Derive final-response scores from unchanged Codex streams without new inference."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from run_claude import sha256
from run_codex import parse_response, summarize


def derive(dataset: Path, source: Path, destination: Path) -> None:
    """Re-extract every saved final response, preserving original records and hashes.

    Args:
        dataset (Path): Frozen data package used only by the scoring parent.
        source (Path): Complete original Codex campaign; never modified.
        destination (Path): New derived campaign directory, which must not exist.
    """
    manifest = json.loads((source / 'manifest.json').read_text())
    records = sorted(source.glob('*/repeat_*/*/record.json'))
    expected = {(model, repeat, case) for model in manifest['models'].values()
                for repeat in range(1, manifest['repeats']+1) for case in manifest['image_sha256']}
    originals = [json.loads(path.read_text()) for path in records]
    actual = [(r['model'], r['repeat'], r['id']) for r in originals]
    if len(actual) != len(expected) or set(actual) != expected:
        raise ValueError('Source campaign must be complete before derivation')
    if destination.exists():
        raise ValueError('Use a new destination to preserve earlier derivations')
    destination.mkdir(parents=True)
    manifest['response_reparse'] = {
        'reason': 'Use last assistant message as final response; preserve preceding commentary',
        'source_manifest_sha256': sha256(source / 'manifest.json'),
        'parser_sha256': sha256(Path(__file__).with_name('run_codex.py')),
        'derivation_sha256': sha256(Path(__file__)),
        'inference_rerun': False,
    }
    for path, original in zip(records, originals, strict=True):
        case = destination / path.parent.relative_to(source)
        case.mkdir(parents=True)
        for filename in ['stdout.jsonl', 'stderr.txt']:
            shutil.copyfile(path.parent / filename, case / filename)
        shutil.copyfile(path, case / 'original_record.json')
        parsed = parse_response((path.parent / 'stdout.jsonl').read_text(),
                                original['returncode'], original['model'])
        record = {**original, **parsed,
                  'original_validation_status': original['status'],
                  'source_record_sha256': sha256(path)}
        (case / 'record.json').write_text(json.dumps(record, indent=2)+'\n')
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    shutil.copyfile(source / 'codex_version.txt', destination / 'codex_version.txt')
    if (source / 'availability.json').exists():
        shutil.copyfile(source / 'availability.json', destination / 'availability.json')
    summarize(dataset, destination, manifest['repeats'], manifest['models'])


def main() -> None:
    """Derive scores from a complete raw campaign without any model invocation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset', type=Path)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    derive(args.dataset.resolve(), args.source.resolve(), args.destination.resolve())


if __name__ == '__main__':
    main()
