#!/usr/bin/env python3
"""Execute robot commands for a poker action.

Translates a poker action into robot primitives, executes them sequentially
via remote_exec, polls frame_diff for completion, and manages execution state.

Usage:
    python3 src/executor.py --action '{"action": "call", "bet_chips": 50}'
    python3 src/executor.py --action '{"action": "call", "bet_chips": 50}' --chips '[...]'
    python3 src/executor.py --cancel-previous
    python3 src/executor.py --cancel-previous --action '{"action": "fold"}'

Output (JSON to stdout):
    {"status": "success", "commands_completed": 2}
    {"status": "failed", "error": "timeout", "commands_completed": 1}
    {"status": "cancelled", "previous_action": {...}}
"""

import argparse
import json
import os
import subprocess
import sys
import time

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_config():
    import yaml
    config_path = os.path.join(SKILL_DIR, "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def _run(script, *args, cwd=None):
    """Run a sibling script and return (stdout, returncode)."""
    cmd = [sys.executable, os.path.join(SRC_DIR, script)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or SKILL_DIR)
    return result.stdout.strip(), result.returncode


def _run_bg(command_str):
    """Run a shell command in the background."""
    subprocess.Popen(
        command_str, shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        cwd=SKILL_DIR,
    )


def _translate(action_json, chips_json=None):
    """Call action_translator to get command sequence."""
    cmd_args = ["--action", action_json]
    if chips_json:
        cmd_args += ["--chips", chips_json]
    stdout, rc = _run("action_translator.py", *cmd_args)
    if rc != 0:
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return None


def _state_cmd(subcommand, *args):
    """Run an execution_state.py subcommand."""
    return _run("execution_state.py", subcommand, *args)


def _remote_exec(*args):
    """Run remote_exec.py with given arguments."""
    return _run("remote_exec.py", *args)


def _capture():
    """Capture a frame and return image path."""
    stdout, rc = _run("capture.py")
    if rc == 0 and stdout:
        return stdout.strip().split("\n")[-1]
    return None


def _frame_diff(path_a, path_b):
    """Compute frame diff between two images. Returns float or None."""
    stdout, rc = _run("frame_diff.py", path_a, path_b)
    if rc == 0 and stdout:
        try:
            return float(stdout.strip())
        except ValueError:
            pass
    return None


def _send_ctrlc():
    """Send Ctrl+C to remote terminal."""
    _remote_exec("--action", "send_ctrlc")


def _cancel_previous(config):
    """Cancel any interrupted execution."""
    stdout, rc = _state_cmd("load")
    if rc != 0 or not stdout:
        return {"status": "cancelled", "previous_action": None}

    try:
        state = json.loads(stdout)
    except json.JSONDecodeError:
        state = {}

    if state.get("phase") in ("executing", "verifying"):
        _send_ctrlc()
        ctrlc_delay = config.get("remote_terminal", {}).get("ctrlc_delay", 0.5)
        time.sleep(ctrlc_delay)

    _state_cmd("clear")
    return {"status": "cancelled", "previous_action": state.get("current_action")}


def _wait_for_stability(config, prev_frame=None):
    """Poll frame_diff until scene is stable. Returns (stable_frame_path, success)."""
    term = config.get("termination", {})
    check_interval = term.get("check_interval", 30)
    threshold = term.get("stability_threshold", 0.03)
    timeout = term.get("timeout", 120)

    start = time.time()
    last_frame = prev_frame

    while time.time() - start < timeout:
        time.sleep(check_interval)
        current_frame = _capture()
        if not current_frame:
            continue

        if last_frame:
            diff = _frame_diff(last_frame, current_frame)
            if diff is not None and diff < threshold:
                return current_frame, True

        last_frame = current_frame

    return last_frame, False


def execute(action_obj, chips=None, config=None, dry_run=False):
    """Execute a full poker action: translate, dispatch, poll, verify."""
    if config is None:
        config = _load_config()

    action_json = json.dumps(action_obj)
    chips_json = json.dumps(chips) if chips else None

    # Translate action to command sequence
    commands = _translate(action_json, chips_json)
    if commands is None:
        return {"status": "failed", "error": "translation_failed", "commands_completed": 0}

    if not commands:
        return {"status": "success", "commands_completed": 0}

    # Dry run — return translated commands without executing
    if dry_run:
        return {"status": "dry_run", "commands": commands}

    # Save execution state
    cmd_names = json.dumps([c.get("command", "") for c in commands])
    _state_cmd(
        "save",
        "--phase", "executing",
        "--action", action_json,
        "--commands", cmd_names,
        "--completed", "0",
        "--round", "0",
    )

    rt = config.get("remote_terminal", {})
    max_retries = rt.get("max_retries", 3)
    retry_delay = rt.get("retry_delay", 1.0)
    ctrlc_delay = rt.get("ctrlc_delay", 0.5)
    cmd_template = config.get("robot", {}).get("command_template", "{command}")
    completed = 0

    # Capture a baseline frame before execution
    baseline_frame = _capture()

    for i, cmd_obj in enumerate(commands):
        is_local = cmd_obj.get("local", False)
        command_str = cmd_obj.get("command", "")

        if is_local:
            # Run locally in background
            _run_bg(command_str)
            completed += 1
            _state_cmd("update", "--completed", str(completed))
            continue

        # Remote command — build policy command from template
        if "args" in cmd_obj:
            policy_cmd = cmd_template.replace("{command}", json.dumps(cmd_obj))
        else:
            policy_cmd = command_str

        success = False
        for attempt in range(max_retries):
            # Execute on remote
            _remote_exec("--action", "execute", "--command", policy_cmd)

            # Wait for robot to finish moving
            stable_frame, stable = _wait_for_stability(config, prev_frame=baseline_frame)

            if stable:
                # Send Ctrl+C to stop the remote process
                _send_ctrlc()
                time.sleep(ctrlc_delay)
                success = True
                baseline_frame = stable_frame
                break
            else:
                # Timeout — retry
                _send_ctrlc()
                time.sleep(ctrlc_delay)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)

        if not success:
            _state_cmd("clear")
            return {
                "status": "failed",
                "error": "timeout",
                "commands_completed": completed,
            }

        completed += 1
        _state_cmd("update", "--completed", str(completed))

    # All commands done
    _state_cmd("clear")
    return {"status": "success", "commands_completed": completed}


def main():
    parser = argparse.ArgumentParser(
        description="Execute robot commands for a poker action.",
        epilog="""
Examples:
  python3 src/executor.py --action '{"action": "call", "bet_chips": 50}'
  python3 src/executor.py --action '{"action": "fold"}'
  python3 src/executor.py --cancel-previous
  python3 src/executor.py --cancel-previous --action '{"action": "check"}'

Output:
  {"status": "success", "commands_completed": 2}
  {"status": "failed", "error": "timeout", "commands_completed": 1}
  {"status": "cancelled", "previous_action": {...}}
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--action",
        default=None,
        help='Poker action JSON, e.g. \'{"action": "call", "bet_chips": 50}\'',
    )
    parser.add_argument(
        "--chips",
        default=None,
        help='Chip inventory JSON, e.g. \'[{"value": 100, "count": 4}]\'',
    )
    parser.add_argument(
        "--cancel-previous",
        action="store_true",
        help="Cancel any interrupted execution before proceeding",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Translate action to commands but skip execution. Prints command sequence.",
    )
    args = parser.parse_args()

    if not args.action and not args.cancel_previous:
        parser.error("either --action or --cancel-previous is required")

    config = _load_config()

    # Cancel previous if requested
    if args.cancel_previous:
        result = _cancel_previous(config)
        if not args.action:
            print(json.dumps(result))
            return

    # Execute new action
    if args.action:
        try:
            action_obj = json.loads(args.action)
        except json.JSONDecodeError as e:
            print(json.dumps({"status": "failed", "error": f"invalid JSON: {e}"}))
            sys.exit(1)

        chips = None
        if args.chips:
            try:
                chips = json.loads(args.chips)
            except json.JSONDecodeError as e:
                print(json.dumps({"status": "failed", "error": f"invalid chips JSON: {e}"}))
                sys.exit(1)

        result = execute(action_obj, chips=chips, config=config, dry_run=args.dry_run)
        print(json.dumps(result))


if __name__ == "__main__":
    main()
