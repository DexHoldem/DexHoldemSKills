"""Tool-free Claude and Gemini adapters for the frozen paired perception task."""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from history_ablation import parse_response as parse_codex, sha

MODELS = {
    'gpt-6-astra': 'codex', 'gpt-6-sol': 'codex', 'gpt-5.6-sol': 'codex',
    'gpt-5.6-luna': 'codex', 'gpt-5.5': 'codex', 'gpt-5.4': 'codex', 'gpt-5.4-mini': 'codex',
    'claude-opus-5-5': 'claude', 'claude-sonnet-5': 'claude', 'claude-opus-4-7': 'claude',
    'claude-sonnet-4-6': 'claude', 'claude-haiku-4-5': 'claude',
    'gemini-3-flash-preview': 'gemini', 'gemini-3.1-flash-lite-preview': 'gemini',
}
GEMINI_SETTINGS = {'tools': {'core': []}, 'mcp': {'allowed': []},
                   'context': {'fileName': '__no_benchmark_memory__.md'}, 'hooksConfig': {'enabled': False}}


def parse_provider(stdout: str, returncode: int, model: str, harness: str,
                   resolved_model: str | None = None) -> dict:
    """Parse exact final JSON, rejecting model mismatches and tool access.

    Args:
        stdout (str): Unmodified provider CLI output.
        returncode (int): Exit status.
        model (str): Requested model ID.
        harness (str): codex, claude or gemini.
        resolved_model (str | None): Explicitly recorded alias target, if approved.

    Returns:
        dict: Prediction/status with raw answer, identity and usage evidence.
    """
    if harness == 'codex':
        return parse_codex(stdout, returncode)
    record = {'status': 'execution_error', 'prediction': None, 'returncode': returncode,
              'resolved_models': [], 'result': None, 'usage': None}
    expected = resolved_model or model
    try:
        if harness == 'claude':
            events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
            results = [e for e in events if isinstance(e, dict) and e.get('type') == 'result']
            init = next((e for e in events if isinstance(e, dict) and e.get('subtype') == 'init'), {})
            result = results[-1] if results else {}
            models = sorted(result.get('modelUsage', {}))
            answer = result.get('result')
            record.update(resolved_models=models, result=answer, usage=result.get('usage'),
                          cost_usd=result.get('total_cost_usd'), errors=result.get('errors'),
                          api_error_status=result.get('api_error_status'))
            if returncode or len(results) != 1 or result.get('is_error', True) or result.get('subtype') != 'success':
                return record
            if init.get('tools') != [] or init.get('mcp_servers') != []:
                record['status'] = 'unexpected_tool_access'
                return record
            if not models or any(m != expected and not m.startswith(expected+'-') for m in models):
                record['status'] = 'model_mismatch'
                return record
        elif harness == 'gemini':
            result = json.loads(stdout)
            stats = result.get('stats', {})
            models = sorted(stats.get('models', {}))
            answer = result.get('response')
            record.update(resolved_models=models, result=answer, usage=stats, errors=result.get('error'))
            if returncode or result.get('error') or not isinstance(answer, str):
                return record
            if stats.get('tools', {}).get('totalCalls') != 0:
                record['status'] = 'unexpected_tool_access'
                return record
            if models != [expected]:
                record['status'] = 'model_mismatch'
                return record
        else:
            raise ValueError(f'Unknown harness: {harness}')
    except (ValueError, KeyError, AttributeError, TypeError):
        return record
    try:
        prediction = json.loads(answer)
        if not isinstance(prediction, dict):
            raise ValueError('Expected one JSON object')
    except (ValueError, TypeError):
        record['status'] = 'invalid_json'
        return record
    record.update(status='completed', prediction=prediction)
    return record


def claude_message(images: list[Path], prompt: str) -> str:
    """Encode chronological unchanged JPEG images (list[Path]) and prompt (str)."""
    content = [{'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg',
                'data': base64.b64encode(image.read_bytes()).decode()}} for image in images]
    content.append({'type': 'text', 'text': prompt})
    return json.dumps({'type': 'user', 'message': {'role': 'user', 'content': content}})+'\n'


def run_provider(repo: Path, output: Path, manifest: dict, pid: str, condition: str,
                 repeat: int, timeout: int) -> dict:
    """Run one isolated Claude/Gemini trial using the frozen shared public inputs.

    Args:
        repo (Path): Image source, never exposed through a tool.
        output (Path): Parent-owned campaign directory.
        manifest (dict): Frozen model/harness and input hashes.
        pid (str): Parent-side problem ID.
        condition (str): Which paired prompt to use.
        repeat (int): One-based repeat index.
        timeout (int): Maximum wall-clock seconds per trial.

    Returns:
        dict: Saved raw-output-derived record; existing records are never replaced.
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
        raise ValueError('Frozen prompt mismatch')
    model, harness = manifest['model'], manifest['harness']
    started = time.time()
    with tempfile.TemporaryDirectory(prefix='dex-paired-'+harness+'-') as work:
        workspace = Path(work)
        images = []
        for index, info in enumerate(entry['images']):
            target = workspace/f'frame_{index:03d}.jpg'
            shutil.copyfile(repo/info['source'], target)
            if sha(target) != info['sha256']:
                raise ValueError('Frozen image mismatch')
            images.append(target)
        env = None
        if harness == 'claude':
            command = ['claude', '-p', '--model', model, '--effort', 'medium',
                       '--input-format', 'stream-json', '--output-format', 'stream-json', '--verbose',
                       '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                       '--safe-mode', '--disable-slash-commands', '--no-session-persistence']
            stdin = claude_message(images, prompt_path.read_text())
        elif harness == 'gemini':
            settings = workspace/'settings.json'
            settings.write_text(json.dumps(GEMINI_SETTINGS))
            env = dict(os.environ, GEMINI_CLI_SYSTEM_SETTINGS_PATH=str(settings), GEMINI_CLI_NO_RELAUNCH='true')
            attachments = '\n'.join('@'+p.name for p in images)
            command = ['gemini', '-p', attachments+'\n'+prompt_path.read_text(), '-m', model,
                       '--output-format', 'json', '--extensions', 'none', '--skip-trust']
            stdin = ''
        else:
            raise ValueError(harness)
        try:
            result = subprocess.run(command, cwd=workspace, env=env, input=stdin, text=True,
                                    capture_output=True, timeout=timeout)
            stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.stdout or b'', exc.stderr or b''
            stdout = stdout.decode(errors='replace') if isinstance(stdout, bytes) else stdout
            stderr = stderr.decode(errors='replace') if isinstance(stderr, bytes) else stderr
            stderr += '\nRunner timeout; no answer selected.\n'
            returncode = 124
    (case/'stdout.jsonl').write_text(stdout)
    (case/'stderr.txt').write_text(stderr)
    record = parse_provider(stdout, returncode, model, harness, manifest.get('resolved_model'))
    # Prompt is already frozen in inputs/: avoid duplicating it in Gemini command metadata.
    stored_command = list(command)
    if harness == 'gemini':
        stored_command[stored_command.index('-p')+1] = '<chronological @frame attachments + frozen prompt>'
    record.update(problem=pid, condition=condition, repeat=repeat, model=model, harness=harness,
                  command=stored_command, prompt_sha256=prompt_info['sha256'],
                  images_sha256=[i['sha256'] for i in entry['images']], started_unix=started,
                  elapsed_s=round(time.time()-started, 3))
    record_path.write_text(json.dumps(record, indent=2)+'\n')
    return record
