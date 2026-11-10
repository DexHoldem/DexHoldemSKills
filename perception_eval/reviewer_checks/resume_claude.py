"""Resume quota-deferred Claude trials using unchanged, frozen provider inputs."""
from __future__ import annotations

import argparse
import fcntl
import json
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from history_ablation import sha
from providers import run_provider

DEFERRED = 'deferred_until_claude_quota_reset'
ZONE = ZoneInfo('Asia/Singapore')


def quota_only(record: dict) -> bool:
    """Identify explicit zero-token quota errors, never a returned model answer.

    Args:
        record (dict): Original adapter record with provider usage metadata.

    Returns:
        bool: Whether a retry can recover a request that produced no answer.
    """
    usage = record.get('usage') or {}
    return (record.get('status') == 'execution_error'
            and record.get('prediction') is None
            and not record.get('resolved_models')
            and '5-hour limit' in str(record.get('result', ''))
            and usage.get('input_tokens') == 0 and usage.get('output_tokens') == 0)


def reset_time(message: str, now: datetime) -> datetime:
    """Resolve an explicit daily reset time; reject unknown reset formats.

    Args:
        message (str): Provider error naming the Asia/Singapore reset time.
        now (datetime): A timezone-aware observation timestamp.

    Returns:
        datetime: Next occurrence of the stated reset, with a one-minute margin.
    """
    match = re.search(r'resets (\d{1,2}):(\d{2})(am|pm) \(Asia/Singapore\)', message)
    if not match:
        raise ValueError(f'Unknown quota reset format: {message}')
    hour, minute = int(match[1]) % 12, int(match[2])
    hour += 12 if match[3] == 'pm' else 0
    local = now.astimezone(ZONE)
    reset = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if reset <= local:
        reset += timedelta(days=1)
    return reset + timedelta(minutes=1)


def pending(root: Path) -> list[Path]:
    """List only deferred or explicitly answer-free Claude quota trials.

    Args:
        root (Path): Shared campaign; other provider records are read-only.

    Returns:
        list[Path]: Canonical records in a deterministic scene/model order.
    """
    paths = []
    for path in (root/'models').glob('claude-*/trials/*/*/*/record.json'):
        raw = json.loads(path.read_text())
        if raw['status'] == DEFERRED or quota_only(raw):
            paths.append(path)
    return sorted(paths, key=lambda p: (int(p.parent.name[1:]), p.parents[4].name,
                                        p.parents[1].name, p.parents[2].name))


def execute(repo: Path, root: Path, stage: Path, path: Path) -> dict:
    """Run a pending trial once and preserve its entire previous evidence.

    Args:
        repo (Path): Read-only dataset repository.
        root (Path): Canonical campaign containing deferred Claude records.
        stage (Path): Unique, durable output directory for this recovery window.
        path (Path): Canonical record selected before invoking the provider.

    Returns:
        dict: Unmodified provider result; malformed answers are not retried.
    """
    prior_sha = sha(path)
    old = json.loads(path.read_text())
    if old['status'] != DEFERRED and not quota_only(old):
        raise ValueError('Refusing to retry a returned answer')
    model_dir = path.parents[4]
    relative = path.parent.relative_to(model_dir/'trials')
    output = stage/model_dir.name
    manifest = json.loads((model_dir/'manifest.json').read_text())
    record = run_provider(repo, output, manifest, old['problem'], old['condition'], old['repeat'], 600)
    if sha(path) != prior_sha:
        raise ValueError('Canonical trial changed during recovery; result retained in staging')
    backup = model_dir/'attempts'/relative/stage.name
    shutil.copytree(path.parent, backup)
    case = output/'trials'/relative
    for source in case.iterdir():
        if source.name != 'record.json' and source.is_file():
            shutil.copyfile(source, path.parent/source.name)
    temporary = path.with_suffix('.publishing')
    shutil.copyfile(case/'record.json', temporary)
    temporary.replace(path)
    evidence = {'previous_record_sha256': prior_sha, 'previous_attempt': str(backup.relative_to(root)),
                'new_record_sha256': sha(path), 'inputs_and_settings_changed': False}
    (case/'recovery.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print('RESULT', old['model'], str(relative), record['status'], flush=True)
    return record


def main() -> None:
    """Wait for quota reset and drain Claude work, pausing on each new quota window."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--not-before', required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    root = args.campaign.resolve()
    with (root/'claude_resume.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        wake = datetime.fromisoformat(args.not_before)
        if wake.tzinfo is None:
            raise ValueError('Resume time must include its timezone')
        while True:
            paths = pending(root)
            state = {'pending': len(paths), 'not_before': wake.isoformat(), 'runner_sha256': sha(Path(__file__)),
                     'updated_unix': time.time(), 'user_authorized_resume': True}
            (root/'claude_resume_status.json').write_text(json.dumps(state, indent=2)+'\n')
            if not paths:
                print('CLAUDE_QUEUE_DRAINED', flush=True)
                return
            print('WAITING_UNTIL', wake.isoformat(), 'pending', len(paths), flush=True)
            while datetime.now(ZONE) < wake:
                time.sleep(min(60, max(0.1, wake.timestamp()-time.time())))
            stage_root = root/'claude_resume_staging'
            stage_root.mkdir(exist_ok=True)
            stage = stage_root/f'quota_resume_{time.time_ns()}'
            stage.mkdir()
            for model in sorted({p.parents[4] for p in paths}):
                output = stage/model.name
                output.mkdir()
                shutil.copytree(model/'inputs', output/'inputs')
                shutil.copyfile(model/'manifest.json', output/'manifest.json')
            quota_records = []
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                for index in range(0, len(paths), args.workers):
                    batch = paths[index:index+args.workers]
                    futures = [pool.submit(execute, args.repo, root, stage, path) for path in batch]
                    records = [future.result() for future in futures]
                    quota_records = [r for r in records if quota_only(r)]
                    state.update(pending=len(pending(root)), updated_unix=time.time())
                    (root/'claude_resume_status.json').write_text(json.dumps(state, indent=2)+'\n')
                    if quota_records:
                        break
            if quota_records:
                wake = max(reset_time(r['result'], datetime.now(ZONE)) for r in quota_records)
            else:
                wake = datetime.now(ZONE)


if __name__ == '__main__':
    main()
