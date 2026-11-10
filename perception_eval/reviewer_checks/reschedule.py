"""Move only unstarted trials into a cache-friendly queue without duplicating calls.

Existing family schedulers are briefly suspended while pending trials receive
reservation records. Their unchanged runners already skip any existing record.
In-flight trials and completed answers are never reserved or interrupted. New
workers execute reserved trials in a staging directory, then atomically replace
the reservation after publishing the raw response artifacts.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import shlex
import signal
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from history_ablation import CONDITIONS, sha
from multi_campaign import invoke, service_failure

RESERVED = 'reserved_for_cache_friendly_queue'


def matches_scheduler(command: str, root: Path) -> bool:
    """Accept only Python executing this exact campaign script and output root."""
    try:
        words = shlex.split(command)
        return (len(words) > 2 and Path(words[0]).name.startswith('python')
                and Path(words[1]).resolve() == Path(__file__).with_name('multi_campaign.py').resolve()
                and Path(words[words.index('--output')+1]).resolve() == root
                and words[words.index('--family')+1] in {'codex', 'claude', 'gemini'})
    except (ValueError, IndexError):
        return False


def family_processes(root: Path) -> list[int]:
    """Find only Python schedulers whose command names this exact campaign root."""
    listing = subprocess.run(['ps', '-axo', 'pid=,comm=,args='], capture_output=True, text=True, check=True).stdout
    found = []
    for line in listing.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) != 3:
            continue
        pid, _executable, command = parts
        if matches_scheduler(command, root):
            found.append(int(pid))
    return found


def reserve(root: Path) -> dict:
    """Reserve only absent trial directories while verified schedulers are paused.

    Args:
        root (Path): Parent directory of the already-frozen per-model campaigns.

    Returns:
        dict: Durable scheduling provenance and every reserved task. Existing
        directories, including calls awaiting responses, remain untouched.
    """
    plan_path = root/'rescheduling.json'
    if plan_path.exists():
        plan = json.loads(plan_path.read_text())
        if plan['runner_sha256'] != sha(Path(__file__)):
            raise ValueError('Rescheduler changed; preserve the original implementation')
        return plan
    processes = family_processes(root)
    if not processes:
        raise ValueError('No verified original schedulers found; do not reserve blindly')
    stopped = []
    tasks = []
    try:
        for pid in processes:
            os.kill(pid, signal.SIGSTOP)
            stopped.append(pid)
        for directory in sorted((root/'models').iterdir()):
            manifest = json.loads((directory/'manifest.json').read_text())
            for repeat in (1, 2, 3):
                for number in range(1, 37):
                    pid = f'p{number}'
                    for condition in CONDITIONS:
                        case = directory/'trials'/condition/f'repeat_{repeat}'/pid
                        if case.exists():
                            continue
                        record = {'status': RESERVED, 'model': manifest['model'], 'problem': pid,
                                  'condition': condition, 'repeat': repeat}
                        tasks.append(record)
        plan = {'runner_sha256': sha(Path(__file__)), 'created_unix': time.time(),
                'reason': 'Group repeats of each model/scene to reuse provider prompt caches; inputs and inference settings unchanged',
                'paused_scheduler_pids': processes, 'inflight_trials_interrupted': 0,
                'reserved_tasks': tasks}
        plan_path.write_text(json.dumps(plan, indent=2)+'\n')
        for record in tasks:
            case = root/'models'/record['model']/'trials'/record['condition']/f"repeat_{record['repeat']}"/record['problem']
            case.mkdir(parents=True)
            (case/'record.json').write_text(json.dumps(record, indent=2)+'\n')
    finally:
        for pid in stopped:
            os.kill(pid, signal.SIGCONT)
    return plan


def publish(staging_case: Path, canonical_case: Path) -> None:
    """Publish raw artifacts, then atomically replace only our reservation record.

    Args:
        staging_case (Path): Completed trial with immutable raw outputs and record.
        canonical_case (Path): Reserved destination observed by the original scheduler.
    """
    old = json.loads((canonical_case/'record.json').read_text())
    if old['status'] != RESERVED:
        raise ValueError(f'Refusing to overwrite an existing answer: {canonical_case}')
    for source in staging_case.iterdir():
        if source.name == 'record.json':
            continue
        if source.is_file():
            shutil.copyfile(source, canonical_case/source.name)
    temp = canonical_case/'record.json.publishing'
    shutil.copyfile(staging_case/'record.json', temp)
    temp.replace(canonical_case/'record.json')


def main() -> None:
    """Reserve unstarted work, then finish grouped trials through unchanged adapters."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=12)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--reserve-only', action='store_true')
    args = parser.parse_args()
    root, repo = args.campaign.resolve(), args.repo.resolve()
    plan = reserve(root)
    print('RESERVED', len(plan['reserved_tasks']), 'unstarted trials; in-flight calls untouched', flush=True)
    if args.reserve_only:
        return
    models = sorted({task['model'] for task in plan['reserved_tasks']})
    manifests = {}
    for model in models:
        canonical = root/'models'/model
        staging = root/'rescheduled_staging'/model
        staging.mkdir(parents=True, exist_ok=True)
        shutil.copytree(canonical/'inputs', staging/'inputs', dirs_exist_ok=True)
        shutil.copyfile(canonical/'manifest.json', staging/'manifest.json')
        manifests[model] = json.loads((canonical/'manifest.json').read_text())
    groups: dict[tuple[str, str], list[dict]] = {}
    for task in plan['reserved_tasks']:
        groups.setdefault((task['model'], task['problem']), []).append(task)
    blocked: set[str] = set()

    def group(model: str, pid: str, tasks: list[dict]) -> None:
        """Run each scene/model's reserved repeats sequentially in fresh sessions."""
        tasks.sort(key=lambda t: (t['repeat'], CONDITIONS.index(t['condition']) if (int(pid[1:])+t['repeat'])%2 else -CONDITIONS.index(t['condition'])))
        for task in tasks:
            if model in blocked:
                return
            relative = Path(task['condition'])/f"repeat_{task['repeat']}"/pid
            canonical_case = root/'models'/model/'trials'/relative
            if not (canonical_case/'record.json').exists():
                # An interrupted reservation phase left this task with the original scheduler.
                continue
            if json.loads((canonical_case/'record.json').read_text())['status'] != RESERVED:
                continue
            staging = root/'rescheduled_staging'/model
            record = invoke(repo, staging, manifests[model], pid, task['condition'], task['repeat'], args.timeout)
            publish(staging/'trials'/relative, canonical_case)
            prior = staging/'attempts'/relative
            if prior.exists():
                shutil.copytree(prior, root/'models'/model/'attempts'/relative, dirs_exist_ok=True)
            reason = service_failure(record, canonical_case)
            if reason in {'quota', 'unavailable_model'}:
                blocked.add(model)
            print('RESULT', model, pid, task['condition'], task['repeat'], record['status'], flush=True)

    ordered = sorted(groups, key=lambda key: (int(key[1][1:]), key[0]))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(group, model, pid, groups[(model, pid)]) for model, pid in ordered]
        for future in as_completed(futures):
            future.result()
    (root/'rescheduled_completion.json').write_text(json.dumps({'blocked_models': sorted(blocked)}, indent=2)+'\n')


if __name__ == '__main__':
    main()
