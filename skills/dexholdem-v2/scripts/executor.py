#!/usr/bin/env python3
"""DexHoldem V2 action executor.

The executor dispatches deterministic robot commands and records progress. It
does not decide the next move and does not mark the dexterous hand idle unless
explicitly asked after visual verification.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from utils import (
    cached_command_for_step,
    extract_json_object,
    first_pending_step,
    load_config,
    loop_safety_limits,
    read_json_file,
    step_status,
    utc_now,
    view_slot_from_intent,
)

SCRIPT_DIR = Path(__file__).resolve().parent


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


def load_current_table():
    info = current_state_info()
    parsed_path = Path(info["state_dir"]) / "01_parsed_state.md"
    if not parsed_path.exists():
        return None
    parsed = extract_json_object(parsed_path.read_text(), predicate=lambda value: isinstance(value.get("table"), dict))
    if not isinstance(parsed, dict):
        return None
    table = parsed.get("table")
    return table if isinstance(table, dict) else None


def load_action_sequence():
    path = Path.cwd() / "action_sequence.json"
    return read_json_file(path, default={}, missing_ok=True)


def continuation_step_for_action(action, sequence):
    """Return the parent-sequence step completed by this action, if any."""
    current_step = sequence.get("current_step") or first_pending_step(sequence)
    if not current_step:
        return None

    name = action.get("action")
    if name == "put_down_card" and current_step in ("put_down_card", "put_down_card_face_up"):
        slot = view_slot_from_intent(sequence.get("intent"))
        if slot and action.get("position", slot) != slot:
            return None
        expected_face_up = current_step == "put_down_card_face_up"
        if bool(action.get("face_up", False)) != expected_face_up:
            return None
        return current_step

    return None


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
    commands = execution.get("commands", translation.get("commands", []))
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


def dispatch_step(step_name, command=None, prefix=None, command_index=None):
    args = ["dispatch-step", "--step", step_name]
    if command:
        args += ["--robot-command", command]
    if prefix is not None:
        args += ["--prefix", prefix or ""]
    if command_index is not None:
        args += ["--command-index", str(command_index)]
    state_cmd(*args)


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


def dispatch_cached_current(dry_run=False):
    config = load_config()
    sequence = load_action_sequence()
    current_step = sequence.get("current_step") or first_pending_step(sequence)
    if not current_step:
        raise RuntimeError("cached sequence has no current step to dispatch")
    status = step_status(sequence, current_step)
    if status == "completed":
        raise RuntimeError(f"current step is already completed: {current_step}")
    if status == "dispatched":
        raise RuntimeError(f"current step is already dispatched and needs visual verification: {current_step}")
    if status != "pending":
        raise RuntimeError(f"current step has unsupported status for dispatch: {current_step}={status}")

    command_index, command, prefix = cached_command_for_step(sequence, current_step)
    plan = sequence.get("plan") or {}
    execution = {
        "stage": "dispatching",
        "started_at": utc_now(),
        "commands": [command],
        "commands_total_in_sequence": len(plan.get("commands") or []),
        "command_index": command_index,
        "commands_dispatched": 0,
        "commands_completed": 0,
        "dry_run": dry_run,
        "can_retry": True,
        "human_required": False,
        "preserved_parent_sequence": True,
        "parent_sequence_id": sequence.get("sequence_id"),
        "parent_intent": sequence.get("intent"),
        "parent_step": current_step,
    }
    action = {
        "action": "continue_sequence",
        "step": current_step,
        "source_action": sequence.get("action"),
    }
    decision = f"Continue cached sequence step `{current_step}`."

    try:
        run_prefix(prefix, config, dry_run)
        if not dry_run:
            remote_exec("--action", "execute", "--command", command)
        execution["commands_dispatched"] = 1
        dispatch_step(current_step, command=command, prefix=prefix, command_index=command_index)
        execution["stage"] = "dispatched"
        execution["completed_at"] = utc_now()
        execution["note"] = "Robot atom command dispatched. Complete the step only after visual atom_idle verification."
        write_action_markdown(action, plan, execution, decision)
        return {"status": "success", "execution": execution, "translation": plan}
    except Exception as exc:
        execution["stage"] = "failed"
        execution["error"] = str(exc)
        state_cmd("fail", "--code", "executor_failed", "--message", str(exc), "--retryable", "true", check=False)
        write_action_markdown(action, plan, execution, f"Execution failed: {exc}")
        return {"status": "failed", "execution": execution, "translation": plan}


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
        reason = action.get("reason", "no reason provided")
        limits = loop_safety_limits(config)
        wait_args = ["record-wait", "--reason", str(reason)]
        if limits["max_consecutive_waits"] is not None:
            wait_args += ["--max-consecutive-waits", str(limits["max_consecutive_waits"])]
        if limits["max_total_waits"] is not None:
            wait_args += ["--max-total-waits", str(limits["max_total_waits"])]
        record = state_cmd(*wait_args)
        wait_record = json.loads(record.stdout)
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
            "wait_counters": (wait_record.get("sequence") or {}).get("safety_counters", {}),
        }
        if wait_record.get("limit_reached"):
            human_action = {
                "action": "request_human",
                "reason": wait_record.get("limit_reason") or "wait limit reached",
                "resume_options": ["inspect_scene", "reset_consecutive_safety", "reset_all_safety", "abort_hand"],
            }
            execution["stage"] = "down"
            execution["human_required"] = True
            execution["limit_reached"] = True
            write_action_markdown(human_action, translation, execution, human_action["reason"])
            return {"status": "human_required", "execution": execution, "translation": translation}
        seconds = float(action.get("sleep_seconds", 0))
        decision = f"Wait for {seconds:g} seconds: {reason}."
        if seconds > 0 and not dry_run and not no_sleep:
            time.sleep(seconds)
        write_action_markdown(action, translation, execution, decision)
        return {"status": "success", "execution": execution, "translation": translation}

    existing_sequence = load_action_sequence()
    continuation_step = continuation_step_for_action(action, existing_sequence)
    if continuation_step:
        parent_status = step_status(existing_sequence, continuation_step)
        if parent_status != "pending":
            raise RuntimeError(f"cannot dispatch continuation step {continuation_step!r} with status {parent_status!r}")
    sequence_cache = translate_sequence_cache(action, chips=chips, table=table)
    translation = sequence_cache.get("plan", {})
    if not continuation_step:
        start_sequence(sequence_cache)

    commands = translation.get("commands", [])
    command_steps = translation.get("command_steps") or []
    dispatch_step_name = continuation_step
    dispatch_command = commands[0] if commands else None
    if dispatch_step_name is None and command_steps:
        dispatch_step_name = command_steps[0]
    execution = {
        "stage": "dispatching",
        "started_at": utc_now(),
        "commands": [dispatch_command] if dispatch_command else [],
        "commands_total_in_sequence": len(commands),
        "command_index": 0 if dispatch_command else None,
        "commands_completed": 0,
        "commands_dispatched": 0,
        "dry_run": dry_run,
        "can_retry": True,
        "human_required": False,
        "preserved_parent_sequence": bool(continuation_step),
    }
    if continuation_step:
        execution["parent_sequence_id"] = existing_sequence.get("sequence_id")
        execution["parent_intent"] = existing_sequence.get("intent")
        execution["parent_step"] = continuation_step

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

        if dispatch_command:
            if not dispatch_step_name:
                raise RuntimeError("translated robot command has no matching sequence step")
            run_prefix(translation.get("prefix"), config, dry_run)
            if not dry_run:
                remote_exec("--action", "execute", "--command", dispatch_command)
            execution["commands_dispatched"] = 1
            dispatch_step(
                dispatch_step_name,
                command=dispatch_command,
                prefix=translation.get("prefix"),
                command_index=0,
            )
            execution["stage"] = "dispatched"
            execution["completed_at"] = utc_now()
            execution["note"] = "Robot atom command dispatched. Complete the step only after visual atom_idle verification."
            if mark_idle:
                execution["mark_idle_ignored"] = True
        else:
            state_cmd("complete-action", "--loop-stage", "idle")
            execution["stage"] = "completed"
            execution["completed_at"] = utc_now()
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
    parser.add_argument("--action", help="Action JSON")
    parser.add_argument("--continue-current", action="store_true", help="Dispatch the current pending command from action_sequence.json")
    parser.add_argument("--chips", help="Chip map JSON")
    parser.add_argument("--table", help="Parsed table JSON; defaults to current 01_parsed_state.md for chip actions")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-sleep", action="store_true")
    parser.add_argument("--mark-idle", action="store_true", help="Only use after visual verification")
    args = parser.parse_args()

    try:
        action = json.loads(args.action) if args.action else None
        chips = json.loads(args.chips) if args.chips else None
        table = json.loads(args.table) if args.table else None
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "failed", "error": f"invalid JSON: {exc}"}))
        raise SystemExit(1)

    try:
        if args.continue_current:
            if args.action:
                raise RuntimeError("--continue-current does not accept --action")
            result = dispatch_cached_current(dry_run=args.dry_run)
        else:
            if action is None:
                raise RuntimeError("--action is required unless --continue-current is used")
            result = execute(
                action,
                chips=chips,
                table=table,
                dry_run=args.dry_run,
                no_sleep=args.no_sleep,
                mark_idle=args.mark_idle,
            )
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2))
        raise SystemExit(1)
    print(json.dumps(result, indent=2))
    if result["status"] == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
