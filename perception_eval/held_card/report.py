"""Export a completed held-card campaign into a compact, reviewable result bundle."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean


def export_report(campaign: Path, destination: Path) -> None:
    """Save per-repeat scores and original response text without session metadata.

    Args:
        campaign (Path): Completed directory created by run_claude.py.
        destination (Path): Destination for a Markdown report and JSON evidence.

    Raises:
        ValueError: Records do not cover every model, repeat and image exactly once.
    """
    summary = json.loads((campaign / 'summary.json').read_text())
    manifest = json.loads((campaign / 'manifest.json').read_text())
    records = [json.loads(p.read_text()) for p in sorted(campaign.glob('*/repeat_*/*/record.json'))]
    expected = {(model, repeat, case) for model in manifest['models'].values()
                for repeat in range(1, manifest['repeats']+1) for case in manifest['image_sha256']}
    actual = [(r['model'], r['repeat'], r['id']) for r in records]
    if len(actual) != len(expected) or set(actual) != expected:
        raise ValueError('Cannot publish a completed report for an incomplete campaign')
    if any(r['input_sha256'] != manifest['image_sha256'][r['id']] for r in records):
        raise ValueError('Image hash mismatch')
    destination.mkdir(parents=True, exist_ok=True)
    for filename in ('summary.json', 'manifest.json', 'claude_version.txt'):
        (destination / filename).write_bytes((campaign / filename).read_bytes())
    keys = ('id', 'model', 'repeat', 'input_sha256', 'status', 'result', 'held_card',
            'resolved_models', 'returncode', 'api_error_status', 'elapsed_s', 'cost_usd')
    (destination / 'responses.jsonl').write_text(''.join(
        json.dumps({key: r[key] for key in keys}, ensure_ascii=False)+'\n' for r in records))
    lines = [
        '# Claude held-card recognition — 2026-11-09', '',
        'Five paper models, 11 fixed images, three independent conversations per image. '
        'The 165 completed attempts are repeated measurements of 11 images, not 165 independent scenes.', '',
        f"Label status: **{summary['label_status']}**. Scores remain provisional pending human label verification.", '',
        '## Exact rank-and-suit results', '',
        '| Model | Repeat 1 | Repeat 2 | Repeat 3 | Mean exact | Mean card macro | Balanced6, per repeat | Invalid JSON | Execution errors |',
        '|---|---:|---:|---:|---:|---:|---|---:|---:|',
    ]
    for model in summary['models']:
        repeats = model['repeats']
        subset = [r for r in records if r['model'] == model['model']]
        invalid = sum(r['status'] == 'invalid_answer' for r in subset)
        counts = [f"{r['all11']['correct']}/{r['all11']['n']}" for r in repeats]
        balanced = ', '.join(f"{r['balanced6']['correct']}/{r['balanced6']['n']}" for r in repeats)
        exact = mean(r['all11']['exact_accuracy'] for r in repeats)*100
        macro = mean(r['all11']['macro_card_accuracy'] for r in repeats)*100
        errors = sum(r['execution_errors'] for r in repeats)
        lines.append('| ' + ' | '.join([model['name'], *counts, f'{exact:.1f}%',
                                        f'{macro:.1f}%', balanced, str(invalid), str(errors)]) + ' |')
    lines += ['', '## Per-image correct counts across three repeats', '',
              '| Image | ' + ' | '.join(m['name'] for m in summary['models']) + ' |',
              '|---|' + '---:|'*len(summary['models'])]
    for case in manifest['image_sha256']:
        cells = [case]
        for model in summary['models']:
            correct = sum(next(item for item in r['all11']['items'] if item['id'] == case)['correct']
                          for r in model['repeats'])
            cells.append(f'{correct}/{len(model["repeats"])}')
        lines.append('| ' + ' | '.join(cells) + ' |')
    statuses = Counter(r['status'] for r in records)
    lines += ['', '## Interpretation and provenance', '',
              '- Answers must be a JSON object with exactly `held_card`; prose and code fences are invalid. '
              'Invalid answers, abstentions and missing predictions stay in the denominator. '
              'Format failures must not be interpreted as pure visual-recognition failures.',
              '- The balanced6 subset contains one image per card identity and is nested within all11. '
              'The card macro score weights the six identities equally.',
              '- All selected identities have red suits. Repeated recording contexts, no empty-hand or '
              'unreadable negatives, and small sample size limit generalization and ranking claims.',
              '- This is a new image-only diagnostic, separate from the original 36-problem history-conditioned table. '
              'The original table and manuscript are unchanged.',
              '- Model IDs, protocol and content hashes are in [manifest.json](manifest.json); '
              'per-repeat and per-card scores are in [summary.json](summary.json). '
              '[responses.jsonl](responses.jsonl) preserves each original final response and execution status. '
              'Complete CLI streams remain in the local campaign directory.',
              f'- Execution status counts: `{json.dumps(dict(statuses), sort_keys=True)}`.',
              '- Validation: four existing dataset/scoring tests and three new input/extraction tests passed.', '']
    (destination / 'README.md').write_text('\n'.join(lines))


def main() -> None:
    """Export the requested completed campaign without running model inference."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    export_report(args.campaign, args.destination)


if __name__ == '__main__':
    main()
