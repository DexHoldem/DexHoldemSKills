"""Evaluate the two paper Gemini models on the frozen held-card image package."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from run_claude import build_message, sha256

MODELS: dict[str, str] = {
    'Gemini 3 Flash': 'gemini-3-flash-preview',
    'Gemini 3.1 Flash Lite': 'gemini-3.1-flash-lite-preview',
}
SETTINGS: dict = {
    'tools': {'core': []},
    'mcp': {'allowed': []},
    'context': {'fileName': '__no_benchmark_memory__.md'},
    'hooksConfig': {'enabled': False},
}


def parse_response(stdout: str, returncode: int, expected_model: str) -> dict:
    """Extract a strict answer while rejecting model fallback and tool use.

    Args:
        stdout (str): Complete unmodified Gemini CLI JSON output.
        returncode (int): Process exit code.
        expected_model (str): Requested model ID, required to match exactly.

    Returns:
        dict: Status, answer, raw final response, model identity and usage.
    """
    out = {'status': 'execution_error', 'held_card': None, 'resolved_models': [],
           'result': None, 'usage': None, 'cost_usd': None, 'returncode': returncode,
           'api_error_status': None}
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return out
    if not isinstance(payload, dict):
        return out
    stats = payload.get('stats', {})
    models = stats.get('models', {})
    out.update(result=payload.get('response'), usage=stats,
               resolved_models=sorted(models), api_error_status=payload.get('error'))
    if returncode or payload.get('error') or not isinstance(payload.get('response'), str):
        return out
    if stats.get('tools', {}).get('totalCalls') != 0:
        out['status'] = 'unexpected_tool_access'
        return out
    if set(models) != {expected_model}:
        out['status'] = 'model_mismatch'
        return out
    try:
        prediction = json.loads(payload['response'])
    except json.JSONDecodeError:
        out['status'] = 'invalid_answer'
        return out
    if not isinstance(prediction, dict) or set(prediction) != {'held_card'}:
        out['status'] = 'invalid_answer'
        return out
    out.update(status='completed', held_card=prediction['held_card'])
    return out


def run_one(root: Path, output: Path, model: str, repeat: int, sample: dict, timeout: int) -> dict:
    """Evaluate one fresh image, retaining raw output and never retrying by score.

    Args:
        root (Path): Frozen package root; private data is never copied to the workspace.
        output (Path): Parent-owned campaign output directory.
        model (str): Exact Gemini model ID.
        repeat (int): One-based repeat index.
        sample (dict): Public id, image path and neutral prompt.
        timeout (int): Maximum process lifetime in seconds.

    Returns:
        dict: Saved result record; existing records are reused unchanged.
    """
    build_message(root, sample)  # Reuse the tested public-field/path validation.
    case = output / model / f'repeat_{repeat}' / sample['id']
    case.mkdir(parents=True, exist_ok=True)
    record_path = case / 'record.json'
    if record_path.exists():
        return json.loads(record_path.read_text())
    command = ['gemini', '-p', '@image.jpg\n'+sample['prompt'], '-m', model,
               '--output-format', 'json', '--extensions', 'none', '--skip-trust']
    started = time.time()
    with tempfile.TemporaryDirectory(prefix='held-card-gemini-') as work:
        directory = Path(work)
        shutil.copyfile(root / sample['image'], directory / 'image.jpg')
        settings_path = directory / 'settings.json'
        settings_path.write_text(json.dumps(SETTINGS))
        env = dict(os.environ, GEMINI_CLI_SYSTEM_SETTINGS_PATH=str(settings_path),
                   GEMINI_CLI_NO_RELAUNCH='true')
        try:
            result = subprocess.run(command, cwd=work, env=env, input='', text=True,
                                    capture_output=True, timeout=timeout)
            stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as error:
            stdout, stderr = error.stdout or b'', error.stderr or b''
            stdout = stdout.decode(errors='replace') if isinstance(stdout, bytes) else stdout
            stderr = stderr.decode(errors='replace') if isinstance(stderr, bytes) else stderr
            stderr += '\nRunner timeout; no answer selected.\n'
            returncode = 124
    (case / 'stdout.json').write_text(stdout)
    (case / 'stderr.txt').write_text(stderr)
    record = parse_response(stdout, returncode, model)
    record.update(id=sample['id'], model=model, repeat=repeat, command=command,
                  input_sha256=sha256(root / sample['image']), started_unix=started,
                  elapsed_s=round(time.time()-started, 3))
    record_path.write_text(json.dumps(record, indent=2)+'\n')
    return record


def summarize(root: Path, output: Path, repeats: int) -> dict:
    """Apply the frozen package scorer to each model/repeat on both subsets.

    Args:
        root (Path): Package containing private labels and its original scorer.
        output (Path): Completed case records and summary destination.
        repeats (int): Number of independent repeats per model.

    Returns:
        dict: Per-repeat metrics with execution errors and label status.
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
    """Run the two original Gemini IDs with matched images, repeats and scoring."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--concurrency', type=int, default=2)
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--summarize-only', action='store_true')
    args = parser.parse_args()
    if min(args.repeats, args.concurrency, args.timeout) < 1:
        parser.error('Repeats, concurrency and timeout must be positive')
    root, output = args.dataset.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    samples = [json.loads(line) for line in (root / 'samples.jsonl').read_text().splitlines()]
    if len({s['id'] for s in samples}) != len(samples):
        raise ValueError('Duplicate sample IDs')
    manifest = {'models': MODELS, 'repeats': args.repeats, 'harness': 'Gemini CLI',
                'effort': 'no override (original Gemini protocol)',
                'cli_version_file': 'gemini_version.txt',
                'validation_tests': 11,
                'input_mode': 'unchanged JPEG via @image.jpg + neutral prompt; no tools/history',
                'settings': SETTINGS,
                'dataset_sha256': sha256(root / 'samples.jsonl'),
                'labels_sha256': sha256(root / 'private/labels.json'),
                'scorer_sha256': sha256(root / 'score.py'),
                'runner_sha256': sha256(Path(__file__)),
                'input_helper_sha256': sha256(Path(__file__).with_name('run_claude.py')),
                'image_sha256': {s['id']: sha256(root / s['image']) for s in samples}}
    manifest_path = output / 'manifest.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != manifest:
        raise ValueError('Campaign configuration changed; choose a new output directory')
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    if not args.summarize_only:
        version = subprocess.run(['gemini', '--version'], capture_output=True, text=True, check=True)
        (output / 'gemini_version.txt').write_text(version.stdout)
        jobs = [(model, rep, sample) for rep in range(1, args.repeats+1)
                for sample in samples for model in MODELS.values()]
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = [pool.submit(run_one, root, output, model, rep, sample, args.timeout)
                       for model, rep, sample in jobs]
            for completed, future in enumerate(as_completed(futures), 1):
                result = future.result()
                print(json.dumps({'finished': completed, 'total': len(jobs),
                                  **{k: result[k] for k in ('model', 'repeat', 'id', 'status')}}), flush=True)
    summarize(root, output, args.repeats)
    print(json.dumps({'summary': str(output / 'summary.json')}))


if __name__ == '__main__':
    main()
