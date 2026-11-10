"""Run all paper model IDs on the frozen paired-history inputs."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from history_ablation import CONDITIONS, run_one, sha
from providers import MODELS, run_provider

# This provider alias was observed in the earlier held-card experiment. Both
# requested and actual IDs are retained; it is never presented as the old snapshot.
RESOLVED_ALIASES = {'gemini-3.1-flash-lite-preview': 'gemini-3.1-flash-lite'}


def prepare_model(source: Path, destination: Path, model: str) -> dict:
    """Freeze model-specific metadata while copying identical predeclared prompts.

    Args:
        source (Path): Original Astra campaign with frozen input texts and hashes.
        destination (Path): One model's new campaign directory.
        model (str): Exact original-paper requested ID.

    Returns:
        dict: Frozen manifest; an existing differing manifest is rejected.
    """
    manifest = json.loads((source/'manifest.json').read_text())
    harness = MODELS[model]
    manifest.update(model=model, harness=harness,
                    backend_identity='requested CLI ID; backend ID absent' if harness == 'codex' else 'provider usage metadata',
                    effort='medium' if harness != 'gemini' else 'provider default; no override',
                    service_tier='fast' if harness == 'codex' else 'provider default',
                    provider_runner_sha256=sha(Path(__file__).with_name('providers.py')),
                    campaign_runner_sha256=sha(Path(__file__)),
                    retry_policy='At most one retry for a service error with no answer; preserve the original attempt. No invalid-answer retries.',
                    resolved_model=RESOLVED_ALIASES.get(model))
    destination.mkdir(parents=True, exist_ok=True)
    path = destination/'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError(f'Frozen configuration changed: {destination}')
    for entry in manifest['problems'].values():
        for prompt in entry['prompts'].values():
            src, dst = source/prompt['path'], destination/prompt['path']
            if sha(src) != prompt['sha256']:
                raise ValueError('Source prompt mismatch')
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() and sha(dst) != prompt['sha256']:
                raise ValueError('Destination prompt mismatch')
            shutil.copyfile(src, dst)
    version = subprocess.run([harness, '--version'], capture_output=True, text=True, check=True).stdout
    version_path = destination/f'{harness}_version.txt'
    if version_path.exists() and version_path.read_text() != version:
        raise ValueError('CLI version changed')
    version_path.write_text(version)
    path.write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def service_failure(record: dict, case: Path) -> str | None:
    """Classify an execution failure from error evidence, never from answer quality."""
    if record['status'] != 'execution_error':
        return None
    if record.get('assistant_messages'):
        return None
    text = (case/'stdout.jsonl').read_text()+'\n'+(case/'stderr.txt').read_text()
    text = text.lower()
    if any(token in text for token in ('usage limit', 'quota exceeded', 'insufficient_quota', 'out of credits')):
        return 'quota'
    if any(token in text for token in ('not supported', 'model_not_found', 'model not found', 'does not exist', 'not have access')):
        return 'unavailable_model'
    if any(token in text for token in ('429', 'rate limit', 'overloaded', '503', '502', 'connection reset', 'connection closed', 'timed out', 'timeout')):
        return 'transient_service'
    return None


def invoke(repo: Path, output: Path, manifest: dict, pid: str, condition: str,
           repeat: int, timeout: int, retry_service: bool = True) -> dict:
    """Execute a trial, with one preserved retry only for a transient no-answer error.

    Args:
        repo/output (Path): Read-only dataset and parent-owned campaign directory.
        manifest (dict): Frozen task and provider configuration.
        pid/condition (str): Problem and input condition.
        repeat/timeout (int): Repetition index and wall-clock limit.
        retry_service (bool): Whether to retry one transient service failure.

    Returns:
        dict: Final trial record. Quota/model-availability failures are not retried.
    """
    runner = run_one if manifest['harness'] == 'codex' else run_provider
    record = runner(repo, output, manifest, pid, condition, repeat, timeout)
    case = output/'trials'/condition/f'repeat_{repeat}'/pid
    reason = service_failure(record, case)
    backup = output/'attempts'/condition/f'repeat_{repeat}'/pid/'attempt_1'
    if retry_service and reason == 'transient_service' and not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(case), str(backup))
        time.sleep(15)
        record = runner(repo, output, manifest, pid, condition, repeat, timeout)
        (case/'retry.json').write_text(json.dumps({'reason': reason, 'prior_attempt': str(backup.relative_to(output))}, indent=2)+'\n')
    return record


def preflight(repo: Path, source: Path, output: Path, model: str, timeout: int) -> dict:
    """Check model access and longest input before scheduling the complete campaign.

    Probes use p1 and p25 annotated inputs and are excluded from formal scores.
    Invalid JSON still proves model access; tool/model mismatch or execution
    failure does not. No gold labels are read by this function.
    """
    destination = output/'probes'/model
    manifest = prepare_model(source, destination, model)
    probes = []
    for pid in ('p1', 'p25'):
        record = invoke(repo, destination, manifest, pid, 'annotated', 1, timeout)
        case = destination/'trials/annotated/repeat_1'/pid
        probes.append({'problem': pid, 'status': record['status'],
                       'resolved_models': record.get('resolved_models', []),
                       'failure': service_failure(record, case)})
        if record['status'] not in {'completed', 'invalid_json'}:
            break
    available = len(probes) == 2 and all(r['status'] in {'completed', 'invalid_json'} for r in probes)
    result = {'model': model, 'harness': MODELS[model], 'available': available,
              'resolved_alias': RESOLVED_ALIASES.get(model), 'probes': probes}
    (destination/'availability.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main() -> None:
    """Preflight every requested original model, then run available configurations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--family', choices=['codex', 'claude', 'gemini'], required=True)
    parser.add_argument('--models', nargs='+')
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    repo, source, output = args.repo.resolve(), args.source.resolve(), args.output.resolve()
    # Astra is already being run in the source campaign and is reused unchanged.
    models = args.models or [m for m, h in MODELS.items() if h == args.family and m != 'gpt-6-astra']
    if any(MODELS[m] != args.family for m in models):
        raise ValueError('Model family mismatch')
    availability = []
    with ThreadPoolExecutor(max_workers=min(args.workers, len(models))) as pool:
        futures = [pool.submit(preflight, repo, source, output, m, args.timeout) for m in models]
        for future in as_completed(futures):
            row = future.result()
            availability.append(row)
            print('PREFLIGHT', json.dumps(row), flush=True)
    (output/f'availability_{args.family}.json').write_text(json.dumps(availability, indent=2)+'\n')
    if args.preflight_only:
        return
    available = [row['model'] for row in availability if row['available']]
    manifests = {m: prepare_model(source, output/'models'/m, m) for m in available}
    blocked: set[str] = set()

    def job(model: str, pid: str, condition: str, repeat: int) -> dict:
        """Run a scheduled trial unless its model exhausted quota during this launch."""
        if model in blocked:
            return {'model': model, 'problem': pid, 'condition': condition, 'repeat': repeat, 'status': 'not_run_quota'}
        directory = output/'models'/model
        record = invoke(repo, directory, manifests[model], pid, condition, repeat, args.timeout)
        reason = service_failure(record, directory/'trials'/condition/f'repeat_{repeat}'/pid)
        if reason in {'quota', 'unavailable_model'}:
            blocked.add(model)
        return record

    jobs = [(m, f'p{n}', c, repeat) for repeat in (1, 2, 3) for n in range(1, 37)
            for m in available for c in (CONDITIONS if (n+repeat)%2 else CONDITIONS[::-1])]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(job, *item) for item in jobs]
        for index, future in enumerate(as_completed(futures), 1):
            record = future.result()
            print('TRIAL', index, '/', len(jobs), record['model'], record['problem'], record['condition'],
                  record['repeat'], record['status'], flush=True)
    (output/f'completion_{args.family}.json').write_text(json.dumps({'models': available, 'blocked': sorted(blocked)}, indent=2)+'\n')


if __name__ == '__main__':
    main()
