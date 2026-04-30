#!/usr/bin/env python3
"""DexHoldem V2 action executor.

The executor dispatches deterministic robot commands and records progress. It
does not decide the next move and does not mark the dexterous hand idle unless
explicitly asked after visual verification.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sibling(name):
    local = Path.cwd() / name
    if local.exists():
        return local
    return SCRIPT_DIR / name


def run_script(name, *args, check=False):
    cmd = [sys.executable, str(sibling(name)), *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"{name} failed")
    return result


def load_config(path="config.yaml"):
    if not Path(path).exists():
        return {}
    try:
        import yaml
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {}


def translate_sequence_cache(action, chips=None, table=None):
    args = ["--action", json.dumps(action), "--as-sequence-cache"]
    if chips is not None:
        args += ["--chips", json.dumps(chips)]
    if table is not None:
        args += ["--table", json.dumps(table)]
    result = run_script("action_translator.py", *args, check=True)
    return json.loads(result.stdout)


def state_cmd(*args, check=True):
    return run_script("state.py", *args, check=check)


def remote_exec(*args, check=True):
    return run_script("remote_exec.py", *args, check=check)


def current_state_info():
    result = state_cmd("current")
    return json.loads(result.stdout)


def current_state_name():
    return current_state_info()["state"]


def extract_json_block(markdown):
    blocks = re.findall(r"```json\s*(.*?)```", markdown, flags=re.S)
    for block in blocks:
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue
    match = re.search(r"(\{.*\})", markdown, flags=re.S)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


def load_current_table():
    info = current_state_info()
    parsed_path = Path(info["state_dir"]) / "01_parsed_state.md"
    if not parsed_path.exists():
        return None
    parsed = extract_json_block(parsed_path.read_text())
    if not isinstance(parsed, dict):
        return None
    table = parsed.get("table")
    return table if isinstance(table, dict) else None


def load_action_sequence():
    path = Path.cwd() / "action_sequence.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def has_chip_inventory(action, chips):
    return chips is not None or action.get("chips") is not None


def should_load_current_table(action, chips, table):
    if table is not None or action.get("table") is not None:
        return False
    name = action.get("action")
    if name == "call":
        return action.get("bet_chips") is None or not has_chip_inventory(action, chips)
    if name == "raise":
        return action.get("bet_chips") is None or not has_chip_inventory(action, chips)
    if name == "all_in":
        return not has_chip_inventory(action, chips)
    if name in ("collect_winnings", "pull_back_chips"):
        return action.get("chip_counts") is None and action.get("pull_chip_counts") is None
    return False


def write_action_markdown(action, translation, execution, decision):
    state_name = current_state_name()
    commands = translation.get("commands", [])
    content = f"""# Action

Based on: `01_parsed_state.md`

## Decision

{decision}

## Action JSON

```json
{json.dumps(action, indent=2)}
```

## Execution

```json
{json.dumps(execution, indent=2)}
```

## Translation

```json
{json.dumps(translation, indent=2)}
```

## Commands

```json
{json.dumps(commands, indent=2)}
```
"""
    tmp = Path(f".{state_name}_action_tmp.md")
    tmp.write_text(content)
    try:
        state_cmd("save-action", "--source", str(tmp))
    finally:
        if tmp.exists():
            tmp.unlink()


def start_sequence(sequence_cache):
    state_cmd("start-action", "--sequence-json", json.dumps(sequence_cache))


def run_prefix(prefix, config, dry_run):
    if not prefix:
        return
    if dry_run:
        return
    rt = config.get("remote_terminal", {}) or {}
    ctrlc_delay = float(rt.get("ctrlc_delay", 0.5))
    if prefix in ("ctrlc", "reset"):
        remote_exec("--action", "send_ctrlc")
        time.sleep(ctrlc_delay)
    if prefix == "reset":
        remote_exec("--action", "click_reset_hand")


def execute(action, chips=None, table=None, dry_run=False, no_sleep=False, mark_idle=False):
    config = load_config()
    name = action.get("action")

    if should_load_current_table(action, chips, table):
        table = load_current_table()

    if name == "wait":
        translation = {"prefix": None, "commands": [], "command_steps": [], "sequence_steps": []}
        commands = []
        sequence = load_action_sequence()
        previous_loop_stage = sequence.get("loop_stage", "idle")
        execution = {
            "stage": "completed",
            "started_at": utc_now(),
            "completed_at": utc_now(),
            "commands": commands,
            "commands_completed": 0,
            "dry_run": dry_run,
            "can_retry": True,
            "human_required": False,
            "preserved_loop_stage": previous_loop_stage,
        }
        seconds = float(action.get("sleep_seconds", 0))
        decision = f"Wait for {seconds:g} seconds: {action.get('reason', 'no reason provided')}."
        if seconds > 0 and not dry_run and not no_sleep:
            time.sleep(seconds)
        write_action_markdown(action, translation, execution, decision)
        return {"status": "success", "execution": execution, "translation": translation}

    sequence_cache = translate_sequence_cache(action, chips=chips, table=table)
    translation = sequence_cache.get("plan", {})
    start_sequence(sequence_cache)

    commands = translation.get("commands", [])
    command_steps = translation.get("command_steps") or []
    execution = {
        "stage": "dispatching",
        "started_at": utc_now(),
        "commands": commands,
        "commands_completed": 0,
        "dry_run": dry_run,
        "can_retry": True,
        "human_required": False,
    }

    decision = f"Execute `{name}`."

    try:
        if name == "request_human":
            reason = action.get("reason", "human help required")
            state_cmd("require-human", "--reason", reason, "--resume-options", ",".join(action.get("resume_options", [])))
            execution["stage"] = "down"
            execution["human_required"] = True
            write_action_markdown(action, translation, execution, reason)
            return {"status": "human_required", "execution": execution, "translation": translation}

        if name == "stop":
            state_cmd("complete-action", "--loop-stage", "idle")
            execution["stage"] = "completed"
            execution["completed_at"] = utc_now()
            write_action_markdown(action, translation, execution, action.get("reason", "Stop."))
            return {"status": "success", "execution": execution, "translation": translation}

        run_prefix(translation.get("prefix"), config, dry_run)

        for index, command in enumerate(commands):
            if not dry_run:
                remote_exec("--action", "execute", "--command", command)
            execution["commands_completed"] += 1
            if index < len(command_steps):
                state_cmd("complete-step", "--step", command_steps[index], check=False)

        execution["stage"] = "dispatched"
        execution["completed_at"] = utc_now()
        execution["note"] = "Robot command dispatched. Agent must verify physical completion from subsequent captures."
        if commands:
            state_cmd("set-loop-stage", "--stage", "idle" if mark_idle else "acting")
        else:
            state_cmd("complete-action", "--loop-stage", "idle")
        write_action_markdown(action, translation, execution, decision)
        return {"status": "success", "execution": execution, "translation": translation}
    except Exception as exc:
        execution["stage"] = "failed"
        execution["error"] = str(exc)
        state_cmd("fail", "--code", "executor_failed", "--message", str(exc), "--retryable", "true", check=False)
        write_action_markdown(action, translation, execution, f"Execution failed: {exc}")
        return {"status": "failed", "execution": execution, "translation": translation}


def main():
    parser = argparse.ArgumentParser(description="Execute a DexHoldem V2 action.")
    parser.add_argument("--action", required=True, help="Action JSON")
    parser.add_argument("--chips", help="Chip map JSON")
    parser.add_argument("--table", help="Parsed table JSON; defaults to current 01_parsed_state.md for chip actions")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-sleep", action="store_true")
    parser.add_argument("--mark-idle", action="store_true", help="Only use after visual verification")
    args = parser.parse_args()

    try:
        action = json.loads(args.action)
        chips = json.loads(args.chips) if args.chips else None
        table = json.loads(args.table) if args.table else None
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "failed", "error": f"invalid JSON: {exc}"}))
        raise SystemExit(1)

    result = execute(
        action,
        chips=chips,
        table=table,
        dry_run=args.dry_run,
        no_sleep=args.no_sleep,
        mark_idle=args.mark_idle,
    )
    print(json.dumps(result, indent=2))
    if result["status"] == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
