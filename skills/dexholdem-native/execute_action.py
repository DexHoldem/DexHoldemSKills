#!/usr/bin/env python3
"""Execute a poker action end-to-end: translate to robot commands and dispatch.

Usage:
    python3 execute_action.py view_card                    # view left card
    python3 execute_action.py view_card --position right   # view right card
    python3 execute_action.py put_down_card                # put down held card
    python3 execute_action.py fold                         # placeholder
    python3 execute_action.py check                        # placeholder
    python3 execute_action.py call --bet-chips 50          # placeholder
    python3 execute_action.py raise --bet-chips 100
    python3 execute_action.py all_in                       # placeholder
"""

import argparse
import json
import os
import subprocess
import sys
import time

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_DIR)

import yaml

from action_translator import translate


def load_config():
    config_path = os.path.join(SKILL_DIR, "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def run_remote_exec(action, **kwargs):
    """Call remote_exec.py as a subprocess."""
    cmd = [sys.executable, os.path.join(SKILL_DIR, "remote_exec.py"), "--action", action]
    for k, v in kwargs.items():
        cmd.extend([f"--{k}", str(v)])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(json.dumps({"status": "error", "remote_action": action, "detail": detail}))
        return False
    return True


def dispatch_commands(commands):
    """Dispatch a list of command dicts from action_translator."""
    ok = True
    for i, cmd in enumerate(commands):
        cmd_str = cmd.get("command", "")
        step = {"step": i + 1, "command": cmd_str}

        if cmd.get("local"):
            subprocess.Popen(cmd_str, shell=True, cwd=SKILL_DIR)
            step.update({"type": "local", "status": "launched"})
            print(json.dumps(step))
            time.sleep(0.5)
        else:
            success = run_remote_exec("execute", command=cmd_str)
            step.update({"type": "remote", "status": "ok" if success else "error"})
            print(json.dumps(step))
            if not success:
                ok = False
    return ok


def execute_view_card(action_obj):
    """Translate and dispatch view_card."""
    commands = translate(action_obj)
    return dispatch_commands(commands)


def execute_put_down_card(config):
    """Send Ctrl+C then click the put-down button (coordinates from config)."""
    pdc = config.get("put_down_card", {})
    x = pdc.get("click_x", 2526)
    y = pdc.get("click_y", 1305)

    ok = run_remote_exec("send_ctrlc")
    if not ok:
        return False

    ctrlc_delay = config.get("remote_terminal", {}).get("ctrlc_delay", 0.5)
    time.sleep(ctrlc_delay)

    ok = run_remote_exec("click", x=x, y=y)
    return ok


def main():
    parser = argparse.ArgumentParser(
        description="Execute a poker action end-to-end (translate + dispatch)."
    )
    parser.add_argument(
        "action",
        choices=["view_card", "put_down_card", "fold", "check", "call", "raise", "all_in"],
        help="Poker action to execute",
    )
    parser.add_argument("--position", default="left", choices=["left", "right"],
                        help="Card position for view_card (default: left)")
    parser.add_argument("--bet-chips", type=int, default=0,
                        help="Chip amount for call/raise")
    parser.add_argument("--chips", default=None,
                        help="Chip inventory JSON for call/raise")
    args = parser.parse_args()

    config = load_config()

    # --- view_card ---
    if args.action == "view_card":
        action_obj = {"action": "view_card", "position": args.position}
        ok = execute_view_card(action_obj)
        sys.exit(0 if ok else 1)

    # --- put_down_card ---
    if args.action == "put_down_card":
        ok = execute_put_down_card(config)
        sys.exit(0 if ok else 1)

    # --- placeholder actions ---
    my_chips = None
    if args.chips:
        try:
            my_chips = json.loads(args.chips)
        except json.JSONDecodeError as e:
            print(json.dumps({"status": "error", "detail": f"bad --chips JSON: {e}"}))
            sys.exit(1)

    action_obj = {"action": args.action}
    if args.action in ("call", "raise"):
        action_obj["bet_chips"] = args.bet_chips

    commands = translate(action_obj, my_chips=my_chips)
    print(json.dumps({
        "status": "not_implemented",
        "action": args.action,
        "translated_commands": [c.get("command") for c in commands],
        "message": f"Action '{args.action}' is not yet connected to a physical robot primitive.",
    }))
    sys.exit(2)


if __name__ == "__main__":
    main()
