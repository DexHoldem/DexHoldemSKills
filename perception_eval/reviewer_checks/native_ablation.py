"""Remove only annotated history/cache files and call unchanged paper runners."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from resume_claude import ZONE, reset_time

MODELS = {
    'gpt-6-astra':'codex', 'gpt-6-sol':'codex', 'gpt-5.6-sol':'codex', 'gpt-5.6-luna':'codex',
    'claude-opus-5-5':'claude', 'claude-sonnet-5':'claude', 'claude-opus-4-7':'claude',
    'claude-sonnet-4-6':'claude', 'claude-haiku-4-5':'claude',
    'gemini-3-flash-preview':'gemini', 'gemini-3.1-flash-lite-preview':'gemini',
}
REMOVED_NAMES = {'01_parsed_state.md', '02_action.md', 'action_sequence.json', 'hole_card_cache.json'}


def digest(path: Path) -> str:
    """Return the SHA-256 of a file at path (Path)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: dict) -> None:
    """Atomically save a dictionary (value) to the JSON file at path (Path)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.writing')
    temporary.write_text(json.dumps(value, indent=2)+'\n')
    temporary.replace(path)


def prepare_problem(source: Path, target: Path) -> dict:
    """Copy unchanged images/links while removing annotated states/actions/caches.

    Args:
        source (Path): One original paper problem directory, with optional runs.
        target (Path): New problem directory outside the original dataset.

    Returns:
        dict: Exact retained/removed input hashes; no labels or old runs copied.
    """
    if target.exists():
        raise ValueError('Refusing to overwrite an existing problem copy')
    target.mkdir(parents=True)
    kept, removed = {}, {}
    for path in sorted(source.iterdir()):
        if path.name in {'runs', '__pycache__'}:
            continue
        if path.name == 's_current' and path.is_symlink():
            link = path.readlink()
            if link.is_absolute() or len(link.parts) != 1 or not re.fullmatch(r's\d+', str(link)):
                raise ValueError('Current-state link must remain within this problem')
            (target/path.name).symlink_to(link)
            kept[path.name] = {'symlink':str(link)}
        elif path.name == '.DS_Store' and path.is_file():
            shutil.copyfile(path, target/path.name)
            kept[path.name] = {'sha256':digest(path)}
        elif path.name in {'action_sequence.json', 'hole_card_cache.json'} and path.is_file():
            removed[path.name] = digest(path)
        elif re.fullmatch(r's\d+', path.name) and path.is_dir() and not path.is_symlink():
            (target/path.name).mkdir()
            for entry in sorted(path.iterdir()):
                relative = entry.relative_to(source).as_posix()
                if entry.name in {'01_parsed_state.md', '02_action.md'} and entry.is_file():
                    removed[relative] = digest(entry)
                elif entry.name == '00_capture.jpg' and entry.is_file() and not entry.is_symlink():
                    shutil.copyfile(entry, target/relative)
                    kept[relative] = {'sha256':digest(entry)}
                else:
                    raise ValueError(f'Unrecognized source input: {entry}')
        else:
            raise ValueError(f'Unrecognized source input: {path}')
    if not (target/'s_current/00_capture.jpg').is_file():
        raise ValueError('Missing current image after copying')
    return {'retained':kept, 'removed':removed}


def prepare(repo: Path, root: Path) -> dict:
    """Freeze 36 ablated problems and exact original runner/guideline hashes.

    Args:
        repo (Path): Original DexHoldem source repository.
        root (Path): Separate output directory for this corrected campaign.

    Returns:
        dict: Frozen provenance; existing campaign inputs must match exactly.
    """
    path = root/'protocol.json'
    if path.exists():
        manifest = json.loads(path.read_text())
        for name, expected in manifest['source_sha256'].items():
            if digest(repo/name) != expected:
                raise ValueError(f'Original source changed: {name}')
        for problem, inputs in manifest['problems'].items():
            target = root/'problems'/problem
            for name, expected in inputs['retained'].items():
                if 'symlink' in expected:
                    if str((target/name).readlink()) != expected['symlink']:
                        raise ValueError('Current image link changed')
                elif digest(target/name) != expected['sha256']:
                    raise ValueError('Image changed')
            if any((target/name).exists() for name in inputs['removed']):
                raise ValueError('Removed annotation reappeared')
        return manifest
    root.mkdir(parents=True, exist_ok=True)
    sources = [repo/'perception_eval'/name for name in
               ('run_codex_benchmark.py','run_claude_benchmark.py','run_gemini_benchmark.py',
                'preflight.py','default_prompt.py','evaluate_column.py')]
    sources += sorted((repo/'skills/dexholdem-v2-native/visual_guidelines').rglob('*.md'))
    if len(sources) <= 6:
        raise ValueError('Native guidelines missing')
    problems = {f'p{i}':prepare_problem(repo/f'bench/problems/p{i}',root/f'problems/p{i}') for i in range(1,37)}
    manifest = {'protocol':'original_paper_native_without_annotations_v1',
                'created_unix':time.time(), 'models':MODELS, 'repeats':3,
                'source_sha256':{str(p.relative_to(repo)):digest(p) for p in sources},
                'problems':problems, 'prompt_changed':False, 'runners_changed':False,
                'tools_changed':False, 'historical_images_retained':True,
                'removed_names':sorted(REMOVED_NAMES),
                'control':'Use the published annotated-history runs; no new annotated control.',
                'retired_models_skipped':['gpt-5.5','gpt-5.4','gpt-5.4-mini']}
    dump(path,manifest)
    return manifest


def command(repo: Path, root: Path, model: str, problem: str, run_id: str) -> list[str]:
    """Build the original single-run invocation without a prompt/tool override.

    Args:
        repo/root (Path): Original source and separate campaign directories.
        model/problem/run_id (str): Requested model, problem, and unique run ID.

    Returns:
        list[str]: Original runner arguments with paper effort/service settings.
    """
    family = MODELS[model]
    cmd = [sys.executable,str(repo/f'perception_eval/run_{family}_benchmark.py'),
           '--problem-dir',str(root/'problems'/problem),'--skill','v2-native',
           '--run-id',run_id,'--model',model,'--reasoning-effort',
           'not_supported' if family == 'gemini' else 'medium',
           '--agent-max-threads','9','--isolation-root',str(root/'workspaces')]
    if family == 'codex':
        cmd += ['--service-tier','fast','--codex-disable','apps','--codex-disable','plugins']
    return cmd


def no_answer_quota(run_dir: Path, family: str) -> str | None:
    """Identify a provider quota failure without replacing an actual answer.

    Args:
        run_dir (Path): Original wrapper's saved artifacts.
        family (str): CLI provider family.

    Returns:
        str | None: Explicit quota message, only for zero-token Claude errors.
    """
    if family != 'claude' or (run_dir/'visual_summary.json').exists():
        return None
    path = run_dir/'claude_stdout.txt'
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except ValueError:
        return None
    usage = data.get('usage') or {}
    text = str(data.get('result',''))
    if (data.get('is_error') and '5-hour limit' in text
            and usage.get('input_tokens') == 0 and usage.get('output_tokens') == 0):
        return text
    return None


def run_trial(repo: Path, root: Path, model: str, problem: str, repeat: int) -> dict:
    """Execute the original runner once, preserving all attempts and artifacts.

    Args:
        repo/root (Path): Original source and separate campaign directories.
        model/problem (str): Requested model and benchmark problem.
        repeat (int): Repetition index, 1 through 3.

    Returns:
        dict: Original wrapper result and provenance; no answer-quality retries.
    """
    trial = root/'records'/model/f'repeat_{repeat}'/problem
    trial.mkdir(parents=True,exist_ok=True)
    path = trial/'record.json'
    if path.exists():
        previous = json.loads(path.read_text())
        if previous['status'] != 'quota_without_answer':
            return previous
    attempt = len(list(trial.glob('attempt_*')))+1
    folder = trial/f'attempt_{attempt}'
    folder.mkdir()
    run_id = f'{problem}_{MODELS[model]}_native_native_noann_{model}_r{repeat}_a{attempt}'
    cmd = command(repo,root,model,problem,run_id)
    dump(folder/'launch.json',{'command':cmd,'started_unix':time.time()})
    with (folder/'stdout.txt').open('w') as stdout, (folder/'stderr.txt').open('w') as stderr:
        result = subprocess.run(cmd,cwd=repo,stdout=stdout,stderr=stderr,check=False)
    try:
        wrapper = json.loads((folder/'stdout.txt').read_text())
    except ValueError:
        wrapper = None
    run_dir = root/'problems'/problem/'runs'/run_id
    quota = no_answer_quota(run_dir,MODELS[model])
    status = 'quota_without_answer' if quota else (wrapper or {}).get('status','wrapper_failed')
    record = {'model':model,'problem':problem,'repeat':repeat,'attempt':attempt,
              'status':status,'returncode':result.returncode,'run_id':run_id,
              'run_dir':str(run_dir),'wrapper_result':wrapper,'quota_message':quota,
              'finished_unix':time.time()}
    dump(folder/'record.json',record)
    dump(path,record)
    print('RESULT',model,problem,repeat,status,flush=True)
    return record


def main() -> None:
    """Run a provider queue, optionally waiting until a known Claude quota reset."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--runner-source',type=Path,help='Exact archived paper source, if different from the dataset repo')
    parser.add_argument('--family',choices=['codex','claude','gemini'])
    parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--not-before')
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--models',nargs='+')
    parser.add_argument('--problems',nargs='+')
    parser.add_argument('--repeats',type=int,nargs='+',default=[1,2,3])
    args=parser.parse_args()
    repo,root=args.repo.resolve(),args.output.resolve()
    prepare(repo,root)
    if args.prepare_only:
        print('PREPARED',root,flush=True)
        return
    runner_repo=args.runner_source.resolve() if args.runner_source else repo
    if args.runner_source:
        historical=json.loads((root/'gpt_paper_provenance.json').read_text())
        for name,expected in historical['snapshot_sha256'].items():
            if digest(runner_repo/name)!=expected:
                raise ValueError(f'Archived runner source mismatch: {name}')
    if not args.family:
        raise ValueError('A provider family is required')
    models=args.models or [m for m,h in MODELS.items() if h==args.family]
    if any(MODELS[m]!=args.family for m in models):
        raise ValueError('Wrong family')
    jobs=[(m,p,r) for r in args.repeats for p in (args.problems or [f'p{i}' for i in range(1,37)]) for m in models]
    with (root/f'{args.family}.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        wake=datetime.fromisoformat(args.not_before) if args.not_before else datetime.now(ZONE)
        prior=root/f'{args.family}_status.json'
        if prior.exists():
            saved=json.loads(prior.read_text()).get('not_before')
            if saved:
                wake=max(wake,datetime.fromisoformat(saved))
        while True:
            pending=[]
            for job in jobs:
                m,p,r=job
                file=root/'records'/m/f'repeat_{r}'/p/'record.json'
                if not file.exists() or json.loads(file.read_text())['status']=='quota_without_answer':
                    pending.append(job)
            dump(prior,{'pending':len(pending),'not_before':wake.isoformat(),'updated_unix':time.time()})
            if not pending:
                print('QUEUE_FINISHED',args.family,flush=True)
                return
            print('PENDING',len(pending),'NOT_BEFORE',wake.isoformat(),flush=True)
            while datetime.now(ZONE)<wake:
                time.sleep(min(60,max(0.1,wake.timestamp()-time.time())))
            quotas=[]
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                for index in range(0,len(pending),args.workers):
                    futures=[pool.submit(run_trial,runner_repo,root,*job) for job in pending[index:index+args.workers]]
                    rows=[future.result() for future in futures]
                    quotas=[row for row in rows if row['status']=='quota_without_answer']
                    if quotas:
                        break
                    if any(row['status']=='wrapper_failed' for row in rows):
                        raise RuntimeError('Wrapper failure: inspect preserved logs before continuing')
            wake=max(reset_time(row['quota_message'],datetime.now(ZONE)) for row in quotas) if quotas else datetime.now(ZONE)


if __name__=='__main__':
    main()
