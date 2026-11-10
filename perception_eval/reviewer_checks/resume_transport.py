"""Resume the same frozen trials at lower concurrency after upload failures."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from history_ablation import sha
from reschedule import RESERVED


def active_rescheduler(root: Path) -> bool:
    """Return whether a Python rescheduler still owns this exact campaign."""
    import shlex
    listing = subprocess.check_output(['ps', '-axo', 'pid=,args='], text=True)
    for line in listing.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) != 2:
            continue
        words = shlex.split(parts[1])
        if (len(words) > 1 and Path(words[0]).name.startswith('python')
            and Path(words[1]).resolve() == Path(__file__).with_name('reschedule.py').resolve()
            and '--campaign' in words and Path(words[words.index('--campaign')+1]).resolve() == root):
            return True
    return False


def recover(root: Path) -> dict:
    """Restore deferred slots and preserve no-answer network failures for one recovery.

    Args:
        root (Path): Campaign with no active original GPT/Gemini scheduler and no
            active rescheduler. Claude quota-deferred slots are left untouched.

    Returns:
        dict: Scheduling-only recovery evidence. No malformed or incorrect answer
        is selected for retry; only timeouts/broken pipes without an answer qualify.
    """
    plan_path = root/'rescheduling.json'
    plan = json.loads(plan_path.read_text())
    existing = {(r['model'],r['problem'],r['condition'],r['repeat']) for r in plan['reserved_tasks']}
    recovered, restored = [], 0
    for model in (root/'models').iterdir():
        if model.name.startswith('claude-'):
            continue
        for path in sorted((model/'trials').glob('*/*/*/record.json')):
            raw = json.loads(path.read_text())
            relative = path.parent.relative_to(model/'trials')
            if raw['status'] == 'deferred_for_lower_upload_concurrency':
                raw['status'] = RESERVED
                path.write_text(json.dumps(raw, indent=2)+'\n')
                restored += 1
                continue
            if raw['status'] != 'execution_error' or raw.get('assistant_messages') or raw.get('result'):
                continue
            evidence = (path.parent/'stdout.jsonl').read_text()+'\n'+(path.parent/'stderr.txt').read_text()
            if not any(token in evidence.lower() for token in ('broken pipe', 'runner timeout', 'stream disconnected')):
                continue
            backup = model/'attempts'/relative/'before_lower_concurrency'
            if backup.exists():
                continue
            shutil.copytree(path.parent, backup)
            staged = root/'rescheduled_staging'/model.name/'trials'/relative
            if (staged/'record.json').exists():
                if sha(staged/'record.json') != sha(path):
                    raise ValueError('Canonical/staged failure mismatch')
                staged.rename(staged.with_name(staged.name+'_before_lower_concurrency'))
            reservation = {'status': RESERVED, **{key:raw[key] for key in ('model','problem','condition','repeat')}}
            path.write_text(json.dumps(reservation, indent=2)+'\n')
            key = (raw['model'],raw['problem'],raw['condition'],raw['repeat'])
            if key not in existing:
                plan['reserved_tasks'].append(reservation)
                existing.add(key)
            recovered.append({'model':model.name,'trial':str(relative),'prior_record_sha256':sha(backup/'record.json'),
                              'reason':'No-answer network failure; preserved before lower-concurrency recovery'})
    if not (root/'rescheduling_before_transport_recovery.json').exists():
        shutil.copyfile(plan_path, root/'rescheduling_before_transport_recovery.json')
    plan_path.write_text(json.dumps(plan, indent=2)+'\n')
    report = {'created_unix':time.time(),'runner_sha256':sha(Path(__file__)),
              'restored_unstarted_trials':restored,'recovered_no_answer_trials':recovered,
              'new_global_concurrency':6,'model_inputs_and_settings_changed':False}
    (root/'transport_recovery.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main() -> None:
    """Wait for current calls to drain, then resume the reserved queue at six workers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--campaign', type=Path, required=True)
    args = parser.parse_args()
    root = args.campaign.resolve()
    while active_rescheduler(root) or any(not (root/f'completion_{family}.json').exists() for family in ('codex','gemini')):
        time.sleep(5)
    report = recover(root)
    print(json.dumps(report), flush=True)
    command = [sys.executable, str(Path(__file__).with_name('reschedule.py')), '--repo', str(args.repo.resolve()),
               '--campaign', str(root), '--workers', '6']
    raise SystemExit(subprocess.run(command, check=False).returncode)


if __name__ == '__main__':
    main()
