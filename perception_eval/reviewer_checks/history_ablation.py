"""Paired, tool-free Codex evaluation with and without annotated history.

All images up to the target frame are identical between conditions. Only
allowlisted prior parsed states and two context caches differ. Gold labels are
never copied into the model workspace or included in a prompt.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

CONDITIONS = ('annotated', 'images_only_history')
DISABLED = ('shell_tool', 'unified_exec', 'apps', 'plugins', 'multi_agent',
            'multi_agent_v2', 'memories', 'hooks', 'skill_search', 'image_generation',
            'view_image', 'browser_use', 'computer_use', 'sleep_tool', 'goals')


def sha(path: Path) -> str:
    """Return the SHA-256 digest of path (Path)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str) -> Any:
    """Load a scoring module at path (Path) under name (str)."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public_inputs(problem: Path) -> tuple[list[Path], list[Path]]:
    """Allowlist images and prior context, excluding target labels and results.

    Args:
        problem (Path): Benchmark problem with s_current pointing to an sN folder.

    Returns:
        tuple[list[Path], list[Path]]: Chronological images through the current
        frame; prior parsed states and existing action/hole-card context caches.
        No future state, current annotation, run output or arbitrary file is read.
    """
    current = (problem/'s_current').resolve()
    if not re.fullmatch(r's\d+', current.name) or current.parent != problem.resolve():
        raise ValueError(f'Invalid target pointer: {problem}')
    target = int(current.name[1:])
    states = sorted((p for p in problem.iterdir() if re.fullmatch(r's\d+', p.name)
                     and p.is_dir() and int(p.name[1:]) <= target), key=lambda p: int(p.name[1:]))
    images, annotations = [], []
    for state in states:
        image = state/'00_capture.jpg'
        if not image.is_file():
            raise ValueError(f'Missing image: {image}')
        images.append(image)
        parsed = state/'01_parsed_state.md'
        if int(state.name[1:]) < target and parsed.is_file():
            annotations.append(parsed)
    for name in ('action_sequence.json', 'hole_card_cache.json'):
        path = problem/name
        if path.is_file():
            annotations.append(path)
    if not images or images[-1].parent.resolve() != current:
        raise ValueError('Current frame must be the last image')
    return images, annotations


def prompt_for(repo: Path, images: list[Path], annotations: list[Path], condition: str) -> str:
    """Build a fixed full-field task with condition-specific prior context.

    Args:
        repo (Path): Source of the shared native field guidelines and schema.
        images (list[Path]): Chronological allowlisted images, target last.
        annotations (list[Path]): Allowlisted prior text/caches, never target labels.
        condition (str): annotated or images_only_history.

    Returns:
        str: Entire model prompt, with no scores or ground truth.
    """
    if condition not in CONDITIONS:
        raise ValueError(condition)
    default = load_module(repo/'perception_eval/default_prompt.py', 'task_schema').DEFAULT_PROMPT
    schema = default.split('Schema for `visual_summary.json`:', 1)[1].split('Do not write null', 1)[0]
    chunks = ['Extract the CURRENT DexHoldem visual state from the attached images. '
              'Images are in chronological order. The LAST image is the target to score; '
              'all earlier images are history. Do not execute actions or choose a poker action. '
              'No tools or external files are available. Any guideline references to files '
              'refer only to supplied content. Never assume an unavailable cache exists.',
              '\nImage order (one-based attachment index):\n' + '\n'.join(
                  f'{i}: {p.parent.name}/00_capture.jpg' + (' [CURRENT TARGET]' if i == len(images) else ' [HISTORY]')
                  for i, p in enumerate(images, 1)), '\nShared field guidelines:']
    for path in sorted((repo/'skills/dexholdem-v2-native/visual_guidelines').glob('*.md')):
        chunks.append(f'\n--- {path.name} ---\n{path.read_text()}')
    chunks.append('\nPRIOR CONTEXT (may be stale; current visual evidence takes priority):')
    if condition == 'annotated':
        for path in annotations:
            name = f'{path.parent.name}/{path.name}' if path.name == '01_parsed_state.md' else path.name
            chunks.append(f'\n--- {name} ---\n{path.read_text()}')
    else:
        chunks.append('No annotated prior states, workflow-state cache, or hole-card/blind cache are provided. '
                      'Use the attached historical and current images to estimate the current fields.')
    chunks.extend(['\nFINAL OUTPUT CONTRACT (overrides individual guideline output formats): '
                   'Return only one JSON object matching the following schema, with no markdown fences. '
                   'Produce concrete estimates, including table.scene_stable; list low-confidence, '
                   'inferred or inherited values in table.uncertain_fields. Do not write files.\n', schema])
    return '\n'.join(chunks)


def command_for(model: str, workspace: Path, images: list[Path]) -> list[str]:
    """Return a fresh tool-free invocation for model and the supplied images."""
    command = ['codex', 'exec', '--ignore-user-config', '--ignore-rules', '--strict-config',
               '--ephemeral', '--skip-git-repo-check', '-s', 'read-only', '-m', model,
               '-c', 'model_reasoning_effort="medium"', '-c', 'service_tier="fast"',
               '-c', 'project_doc_max_bytes=0', '-c', 'web_search="disabled"',
               '--enable', 'skip_host_skill_discovery']
    for feature in DISABLED:
        command += ['--disable', feature]
    command += ['--json', '-C', str(workspace)]
    for image in images:
        command += ['-i', str(image)]
    return command + ['-']


def parse_response(stdout: str, returncode: int) -> dict:
    """Parse strict final JSON after one completed tool-free turn.

    Args:
        stdout (str): Unmodified Codex JSONL events.
        returncode (int): CLI exit code.

    Returns:
        dict: Status, raw messages, usage and structured prediction if valid.
        Earlier progress messages are retained but never used as the answer.
    """
    record = {'status': 'execution_error', 'prediction': None, 'returncode': returncode}
    try:
        events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
        completed = [e for e in events if e.get('type') == 'turn.completed']
        items = [e['item'] for e in events if e.get('type') == 'item.completed']
        messages = [i['text'] for i in items if i.get('type') == 'agent_message']
        errors = [e for e in events if e.get('type') in {'error', 'turn.failed'}]
        warnings = [i.get('message', '') for i in items if i.get('type') == 'error']
    except (ValueError, KeyError, TypeError, AttributeError):
        return record
    record.update(assistant_messages=messages, errors=errors, warnings=warnings,
                  usage=completed[-1].get('usage') if completed else None)
    if returncode or len(completed) != 1 or errors or not messages:
        return record
    if any(e.get('item', {}).get('type') not in {'agent_message', 'reasoning', 'error'}
           for e in events if e.get('type') in {'item.started', 'item.updated', 'item.completed'}):
        record['status'] = 'unexpected_tool_access'
        return record
    if any('fallback' in str(w).lower() or 'will be omitted' in str(w).lower() for w in warnings):
        record['status'] = 'configuration_mismatch'
        return record
    try:
        prediction = json.loads(messages[-1])
        if not isinstance(prediction, dict):
            raise ValueError('Expected object')
    except (ValueError, TypeError):
        record['status'] = 'invalid_json'
        return record
    record.update(status='completed', prediction=prediction)
    return record


def prepare(repo: Path, output: Path, model: str, repeats: int) -> dict:
    """Freeze prompts and input hashes before any inference or scoring.

    Existing manifests must match, preventing accidental protocol changes on
    resume. Returns a JSON-serializable manifest for repo/output (Path), exact
    requested model (str), and independent repeat count (int).
    """
    problems = {}
    for number in range(1, 37):
        pid = f'p{number}'
        images, annotations = public_inputs(repo/'bench/problems'/pid)
        entry = {'images': [{'source': str(p.relative_to(repo)), 'sha256': sha(p)} for p in images],
                 'prior_context': [{'source': str(p.relative_to(repo)), 'sha256': sha(p)} for p in annotations],
                 'prompts': {}}
        for condition in CONDITIONS:
            prompt = prompt_for(repo, images, annotations, condition)
            path = output/'inputs'/pid/f'{condition}.txt'
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and path.read_text() != prompt:
                raise ValueError(f'Frozen prompt changed: {path}')
            path.write_text(prompt)
            entry['prompts'][condition] = {'path': str(path.relative_to(output)), 'sha256': sha(path)}
        problems[pid] = entry
    manifest = {'protocol': 'paired_history_ablation_v1', 'model': model,
                'backend_identity': 'Requested CLI model ID; backend ID not exposed in JSONL',
                'effort': 'medium', 'service_tier': 'fast', 'repeats': repeats,
                'conditions': list(CONDITIONS), 'problems': problems,
                'runner_sha256': sha(Path(__file__)),
                'guidelines': {p.name: sha(p) for p in sorted((repo/'skills/dexholdem-v2-native/visual_guidelines').glob('*.md'))}}
    path = output/'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError('Manifest mismatch: use a new output directory')
    path.write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def run_one(repo: Path, output: Path, manifest: dict, pid: str, condition: str,
            repeat: int, timeout: int) -> dict:
    """Run one frozen trial with no score-based retries, retaining raw evidence.

    Args:
        repo (Path): Image source only; never made available to the child model.
        output (Path): Parent-owned inputs and results.
        manifest (dict): Frozen public inputs and model configuration.
        pid (str): Original problem ID, used only in parent-side bookkeeping.
        condition (str): Which frozen prompt to send.
        repeat (int): One-based independent repeat.
        timeout (int): Wall-clock limit in seconds.

    Returns:
        dict: Immutable trial record, including any invalid or failed response.
    """
    case = output/'trials'/condition/f'repeat_{repeat}'/pid
    case.mkdir(parents=True, exist_ok=True)
    record_path = case/'record.json'
    if record_path.exists():
        return json.loads(record_path.read_text())
    entry = manifest['problems'][pid]
    prompt_info = entry['prompts'][condition]
    prompt_path = output/prompt_info['path']
    if sha(prompt_path) != prompt_info['sha256']:
        raise ValueError('Prompt changed since freezing')
    started = time.time()
    with tempfile.TemporaryDirectory(prefix='dex-history-') as work:
        workspace = Path(work)
        images = []
        for index, info in enumerate(entry['images']):
            source = repo/info['source']
            target = workspace/f'frame_{index:03d}.jpg'
            shutil.copyfile(source, target)
            if sha(target) != info['sha256']:
                raise ValueError('Image changed since freezing')
            images.append(target)
        command = command_for(manifest['model'], workspace, images)
        try:
            result = subprocess.run(command, cwd=workspace, input=prompt_path.read_text(),
                                    capture_output=True, text=True, timeout=timeout)
            stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.stdout or b'', exc.stderr or b''
            stdout = stdout.decode(errors='replace') if isinstance(stdout, bytes) else stdout
            stderr = stderr.decode(errors='replace') if isinstance(stderr, bytes) else stderr
            stderr += '\nRunner timeout; no answer selected.\n'
            returncode = 124
    (case/'stdout.jsonl').write_text(stdout)
    (case/'stderr.txt').write_text(stderr)
    record = parse_response(stdout, returncode)
    record.update(problem=pid, condition=condition, repeat=repeat, model=manifest['model'],
                  command=command, prompt_sha256=prompt_info['sha256'],
                  images_sha256=[i['sha256'] for i in entry['images']],
                  started_unix=started, elapsed_s=round(time.time()-started, 3))
    record_path.write_text(json.dumps(record, indent=2)+'\n')
    return record


def main() -> None:
    """Prepare a frozen protocol, then execute selected independent trials."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model', default='gpt-6-astra')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    manifest = prepare(repo, output, args.model, args.repeats)
    if args.prepare_only:
        print('Prepared', len(manifest['problems']), 'problems', flush=True)
        return
    version = subprocess.run(['codex', '--version'], capture_output=True, text=True, check=True).stdout
    version_path = output/'codex_version.txt'
    if version_path.exists() and version_path.read_text() != version:
        raise ValueError('CLI version changed')
    version_path.write_text(version)
    # Alternate pair order by problem/repeat to avoid fixed condition-order bias.
    jobs = [(f'p{n}', c, repeat) for repeat in range(1, args.repeats+1)
            for n in range(1, 37) for c in (CONDITIONS if (n+repeat)%2 else CONDITIONS[::-1])]
    if args.limit:
        jobs = jobs[:args.limit]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, repo, output, manifest, pid, c, r, args.timeout) for pid, c, r in jobs]
        for index, future in enumerate(as_completed(futures), 1):
            record = future.result()
            print(index, '/', len(jobs), record['problem'], record['condition'],
                  record['repeat'], record['status'], record['elapsed_s'], flush=True)


if __name__ == '__main__':
    main()
