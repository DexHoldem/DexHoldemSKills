#!/usr/bin/env python3
"""Remote terminal execution client.

Sends HTTP requests to a PyAutoGUI service running on the remote machine.
The remote service exposes /exec and /batch endpoints that proxy pyautogui/pyperclip calls.
Used by the texas-holdem-robot skill to execute robot policy commands.
"""

import argparse
import json
import os
import urllib.request
import urllib.error

import yaml


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_base_url(args, config):
    if args.host:
        return args.host.rstrip("/")
    rt = config.get("remote_terminal", {})
    host = rt.get("host", "http://localhost:5000")
    return host.rstrip("/")


def post_request(base_url, endpoint, payload):
    url = f"{base_url}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            print(json.dumps(body))
            return body
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(json.dumps({"status": "error", "code": e.code, "detail": error_body}))
        raise SystemExit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"status": "error", "detail": str(e.reason)}))
        raise SystemExit(1)


def action_execute(args, config):
    base_url = get_base_url(args, config)
    rt = config.get("remote_terminal", {})
    click_x = rt.get("click_x", 500)
    click_y = rt.get("click_y", 300)
    focus_delay = rt.get("focus_delay", 0.3)
    payload = {
        "actions": [
            {"action": "click", "args": [click_x, click_y]},
            {"sleep": focus_delay},
            {"action": "pyperclip.copy", "args": [args.command]},
            {"action": "hotkey", "args": ["ctrl", "shift", "v"]},
            {"sleep": 0.1},
            {"action": "press", "args": ["enter"]},
        ]
    }
    post_request(base_url, "/batch", payload)


def action_send_ctrlc(args, config):
    base_url = get_base_url(args, config)
    rt = config.get("remote_terminal", {})
    click_x = rt.get("click_x", 500)
    click_y = rt.get("click_y", 300)
    payload = {
        "actions": [
            {"action": "click", "args": [click_x, click_y]},
            {"sleep": 0.2},
            {"action": "hotkey", "args": ["ctrl", "c"]},
        ]
    }
    post_request(base_url, "/batch", payload)


def action_click(args, config):
    base_url = get_base_url(args, config)
    payload = {
        "actions": [
            {"action": "click", "args": [args.x, args.y]},
        ]
    }
    post_request(base_url, "/batch", payload)


def action_click_reset_hand(args, config):
    """Click the reset-hand GUI button. Reads coords from config['reset_hand']."""
    base_url = get_base_url(args, config)
    rh = config.get("reset_hand", {})
    if "click_x" not in rh or "click_y" not in rh:
        print(json.dumps({
            "status": "error",
            "detail": "reset_hand.click_x / click_y missing from config",
        }))
        raise SystemExit(1)
    payload = {
        "actions": [
            {"action": "click", "args": [rh["click_x"], rh["click_y"]]},
        ]
    }
    post_request(base_url, "/batch", payload)


def action_calibrate(args, config):
    base_url = get_base_url(args, config)
    post_request(base_url, "/exec", {"action": "position"})


def main():
    parser = argparse.ArgumentParser(
        description="Send commands to remote PyAutoGUI terminal service"
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["execute", "send_ctrlc", "click", "click_reset_hand", "calibrate"],
        help="Action to perform",
    )
    parser.add_argument("--command", help="Shell command to paste (required for execute)")
    parser.add_argument("--x", type=int, help="X coordinate (for click action)")
    parser.add_argument("--y", type=int, help="Y coordinate (for click action)")
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml"),
        help="Path to config.yaml",
    )
    parser.add_argument("--host", help="Override remote service URL (e.g. http://192.168.1.50:5000)")
    args = parser.parse_args()

    if args.action == "execute" and not args.command:
        parser.error("--command is required for execute action")
    if args.action == "click" and (args.x is None or args.y is None):
        parser.error("--x and --y are required for click action")

    config = {}
    if os.path.exists(args.config):
        config = load_config(args.config)

    actions = {
        "execute": action_execute,
        "send_ctrlc": action_send_ctrlc,
        "click": action_click,
        "click_reset_hand": action_click_reset_hand,
        "calibrate": action_calibrate,
    }
    actions[args.action](args, config)


if __name__ == "__main__":
    main()
