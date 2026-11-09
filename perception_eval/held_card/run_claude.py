"""Run fresh, tool-free Claude conversations on the frozen held-card package."""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

MODELS: dict[str, str] = {
    'Opus 5.5': 'claude-opus-5-5',
    'Sonnet 5': 'claude-sonnet-5',
    'Opus 4.7': 'claude-opus-4-7',
    'Sonnet 4.6': 'claude-sonnet-4-6',
    'Haiku 4.5': 'claude-haiku-4-5',
}


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file at path (Path)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_message(root: Path, sample: dict) -> str:
    """Encode only one sample's unchanged JPEG bytes and neutral prompt.

    Args:
        root (Path): Dataset package root, never provided to the model.
        sample (dict): Public id, image relative path, and prompt record.

    Returns:
        str: One newline-terminated Claude stream-json user message.

    Raises:
        ValueError: Input record contains unexpected fields or escapes inputs/.
    """
    if set(sample) != {'id', 'image', 'prompt'}:
        raise ValueError('Only public sample fields are allowed')
    image = (root / sample['image']).resolve()
    if not image.is_relative_to((root / 'inputs').resolve()):
        raise ValueError('Image must be inside the public input directory')
    content = [
        {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg',
                                   'data': base64.b64encode(image.read_bytes()).decode()}},
        {'type': 'text', 'text': sample['prompt']},
    ]
    return json.dumps({'type': 'user', 'message': {'role': 'user', 'content': content}}) + '\n'


def parse_response(stdout: str, returncode: int, expected_model: str) -> dict:
    """Parse one complete response without searching prose for a favorable card.

    Args:
        stdout (str): Unmodified JSONL output of Claude Code.
        returncode (int): CLI process exit code.
        expected_model (str): Explicit requested model ID.

    Returns:
        dict: Execution status, strict JSON prediction, resolved models and usage.
    """
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    results = [e for e in events if isinstance(e, dict) and e.get('type') == 'result']
    init = next((e for e in events if isinstance(e, dict) and e.get('subtype') == 'init'), {})
    result = results[-1] if results else {}
    resolved = sorted(result.get('modelUsage', {}))
    out = {'status': 'execution_error', 'held_card': None, 'resolved_models': resolved,
           'result': result.get('result'), 'usage': result.get('usage'),
           'cost_usd': result.get('total_cost_usd'), 'returncode': returncode,
           'api_error_status': result.get('api_error_status')}
    if returncode or result.get('is_error', True) or result.get('subtype') != 'success':
        return out
    if init.get('tools') != [] or init.get('mcp_servers') != []:
        out['status'] = 'unexpected_tool_access'
        return out
    if not resolved or any(m != expected_model and not m.startswith(expected_model + '-') for m in resolved):
        out['status'] = 'model_mismatch'
        return out
    try:
        prediction = json.loads(result.get('result', ''))
    except (json.JSONDecodeError, TypeError):
        out['status'] = 'invalid_answer'
        return out
    if not isinstance(prediction, dict) or set(prediction) != {'held_card'}:
        out['status'] = 'invalid_answer'
        return out
    out.update(status='completed', held_card=prediction['held_card'])
    return out


def run_one(root: Path, output: Path, model: str, repeat: int, sample: dict, timeout: int) -> dict:
    """Run one model/repeat/sample, saving raw output before extracting its answer.

    Args:
        root (Path): Frozen dataset root.
        output (Path): Campaign result directory, never accessible through tools.
        model (str): Explicit Claude model identifier.
        repeat (int): One-based independent repeat index.
        sample (dict): Public input record.
        timeout (int): Maximum seconds for this CLI call.

    Returns:
        dict: Persistent completion or failure record; existing records are reused.
    """
    case = output / model / f'repeat_{repeat}' / sample['id']
    case.mkdir(parents=True, exist_ok=True)
    record_path = case / 'record.json'
    if record_path.exists():
        return json.loads(record_path.read_text())
    command = ['claude', '-p', '--model', model, '--effort', 'medium',
               '--input-format', 'stream-json', '--output-format', 'stream-json', '--verbose',
               '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
               '--safe-mode', '--disable-slash-commands', '--no-session-persistence']
    started = time.time()
    with tempfile.TemporaryDirectory(prefix='held-card-input-') as work:
        try:
            result = subprocess.run(command, input=build_message(root, sample), cwd=work,
                                    text=True, capture_output=True, timeout=timeout)
            stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or b''
            stderr = error.stderr or b''
            stdout = stdout.decode(errors='replace') if isinstance(stdout, bytes) else stdout
            stderr = stderr.decode(errors='replace') if isinstance(stderr, bytes) else stderr
            stderr += '\nRunner timeout; no answer selected.\n'
            returncode = 124
    (case / 'stdout.jsonl').write_text(stdout)
    (case / 'stderr.txt').write_text(stderr)
    record = parse_response(stdout, returncode, model)
    record.update(id=sample['id'], model=model, repeat=repeat, command=command,
                  input_sha256=sha256(root / sample['image']), started_unix=started,
                  elapsed_s=round(time.time()-started, 3))
    record_path.write_text(json.dumps(record, indent=2) + '\n')
    return record


def summarize(root: Path, output: Path, repeats: int) -> dict:
    """Use the package's existing offline scorer on both fixed subsets.

    Args:
        root (Path): Package containing evaluator-only labels and score.py.
        output (Path): Campaign records and generated score destinations.
        repeats (int): Number of independent runs per model.

    Returns:
        dict: Per-repeat metrics, completion counts and label provenance.
    """
    spec = importlib.util.spec_from_file_location('held_card_score', root / 'score.py')
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    gold = json.loads((root / 'private/labels.json').read_text())
    subsets = json.loads((root / 'private/subsets.json').read_text())
    report = {'label_status': gold['label_status'], 'models': []}
    for name, model in MODELS.items():
        row = {'name': name, 'model': model, 'repeats': []}
        for repeat in range(1, repeats+1):
            directory = output / model / f'repeat_{repeat}'
            directory.mkdir(parents=True, exist_ok=True)
            records = [json.loads(p.read_text()) for p in sorted(directory.glob('*/record.json'))]
            predictions = [{'id': r['id'], 'held_card': r['held_card']} for r in records
                           if r['status'] in {'completed', 'invalid_answer'}]
            (directory / 'predictions.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in predictions))
            metrics = {'repeat': repeat, 'finished': len(records),
                       'execution_errors': sum(r['status'] not in {'completed', 'invalid_answer'} for r in records)}
            for subset, ids in subsets.items():
                metrics[subset] = scorer.score([r for r in gold['items'] if r['id'] in ids],
                                              [p for p in predictions if p['id'] in ids])
            (directory / 'scores.json').write_text(json.dumps(metrics, indent=2)+'\n')
            row['repeats'].append(metrics)
        report['models'].append(row)
    (output / 'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main() -> None:
    """Run the five paper Claude configurations with resumable independent cases."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--concurrency', type=int, default=2)
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--summarize-only', action='store_true')
    args = parser.parse_args()
    if min(args.repeats, args.concurrency, args.timeout) < 1:
        parser.error('Repeats, concurrency, and timeout must be positive')
    root, output = args.dataset.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    samples = [json.loads(line) for line in (root / 'samples.jsonl').read_text().splitlines()]
    if len({s['id'] for s in samples}) != len(samples):
        raise ValueError('Duplicate sample IDs')
    manifest = {'models': MODELS, 'repeats': args.repeats, 'effort': 'medium',
                'input_mode': 'unmodified JPEG + neutral prompt; no tools/history',
                'dataset_sha256': sha256(root / 'samples.jsonl'),
                'labels_sha256': sha256(root / 'private/labels.json'),
                'scorer_sha256': sha256(root / 'score.py'),
                'runner_sha256': sha256(Path(__file__)),
                'image_sha256': {s['id']: sha256(root / s['image']) for s in samples}}
    manifest_path = output / 'manifest.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != manifest:
        raise ValueError('Campaign configuration changed; use a new output directory')
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    if not args.summarize_only:
        version = subprocess.run(['claude', '--version'], capture_output=True, text=True, check=True)
        (output / 'claude_version.txt').write_text(version.stdout)
        jobs = [(model, rep, sample) for rep in range(1, args.repeats+1)
                for sample in samples for model in MODELS.values()]
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = [pool.submit(run_one, root, output, model, rep, sample, args.timeout)
                       for model, rep, sample in jobs]
            for completed, future in enumerate(as_completed(futures), 1):
                result = future.result()
                print(json.dumps({'finished': completed, 'total': len(jobs),
                                  **{k: result[k] for k in ('model', 'repeat', 'id', 'status')}}), flush=True)
    report = summarize(root, output, args.repeats)
    print(json.dumps({'summary': str(output / 'summary.json'), 'models': len(report['models'])}))


if __name__ == '__main__':
    main()
