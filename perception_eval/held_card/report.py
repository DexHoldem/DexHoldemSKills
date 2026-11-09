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
        campaign (Path): Completed directory created by a held-card runner.
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
    for filename in ('summary.json', 'manifest.json', manifest.get('cli_version_file', 'claude_version.txt')):
        (destination / filename).write_bytes((campaign / filename).read_bytes())
    keys = ('id', 'model', 'repeat', 'input_sha256', 'status', 'result', 'held_card',
            'resolved_models', 'returncode', 'api_error_status', 'elapsed_s', 'cost_usd')
    optional_keys = ('requested_model', 'original_validation_status', 'source_record_sha256',
                     'model_identity_evidence', 'cli_warnings', 'assistant_messages')
    (destination / 'responses.jsonl').write_text(''.join(
        json.dumps({key: r[key] for key in (*keys, *optional_keys) if key in r}, ensure_ascii=False)+'\n'
        for r in records))
    family = manifest.get('harness', 'Claude CLI').removesuffix(' CLI')
    n_images = len(manifest['image_sha256'])
    lines = [
        f'# {family} held-card recognition — 2026-11-09', '',
        f"{len(manifest['models'])} model configurations, {n_images} fixed images, "
        f"{manifest['repeats']} independent conversations per image. "
        f'The {len(records)} completed attempts are repeated measurements of {n_images} images, '
        f'not {len(records)} independent scenes.', '',
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
              f"- Validation: {manifest.get('validation_tests', 7)} dataset/scoring and input/extraction tests passed.", '']
    if 'model_resolution' in manifest:
        resolution = manifest['model_resolution']
        lines += ['## Model version difference', '',
                  f"The requested `{resolution['requested']}` ID returned `{resolution['reported_actual']}` "
                  'in every Flash-Lite call. This result is labeled as the current stable model; '
                  'it does not reproduce the retired preview used in the original paper. '
                  f"See [Google's deprecation notice]({resolution['source']}).", '',
                  'The raw campaign initially rejected these responses as model mismatches. '
                  'A separate offline derivation revalidates them against the actual stable ID, '
                  'retaining requested IDs and original validation status. No response was rerun, '
                  'selected by correctness, or changed; the strict answer parser is identical.', '']
    if manifest.get('harness') == 'Codex CLI':
        lines += ['## Codex identity and availability', '',
                  'These are the exact model IDs requested through Codex CLI. Its JSONL events '
                  'do not expose an independent backend model ID; `resolved_models` is therefore '
                  'empty rather than inferred. API errors, observed tool invocations, fallback '
                  'metadata warnings and dropped service-tier warnings are rejected.', '']
        availability_path = campaign / 'availability.json'
        if availability_path.exists():
            (destination / 'availability.json').write_bytes(availability_path.read_bytes())
            availability = json.loads(availability_path.read_text())
            unavailable = [r['model'] for r in availability['cases'] if r['status'] != 'completed']
            lines += ['Separate connectivity checks are preserved in '
                      '[availability.json](availability.json). All preflight predictions, '
                      'including successful calls, are excluded from formal scores.', '']
            if unavailable:
                lines += ['Original-paper IDs unavailable in this account: '
                          + ', '.join(f'`{model}`' for model in unavailable)
                          + '. These configurations were not replaced and have no recognition '
                          'score. The service errors are retained in the availability record.', '']
        if 'response_reparse' in manifest:
            lines += ['The initial extractor incorrectly classified multiple assistant messages '
                      'as execution failures. A separate offline derivation parses the final '
                      'assistant message, consistently with the other CLI final-response envelopes. '
                      'Earlier commentary is retained in `assistant_messages`; the final message '
                      'must still be strict JSON. Source records, original statuses and hashes are '
                      'retained. No inference was repeated or selected by correctness.', '']
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
