#!/usr/bin/env python3
"""Remote PyAutoGUI terminal client for DexHoldem V2."""

import argparse
import json
import urllib.error
import urllib.request

from utils import load_config


def base_url(args, config):
    if args.host:
        return args.host.rstrip("/")
    return (config.get("remote_terminal", {}) or {}).get("host", "http://localhost:5000").rstrip("/")


def request_timeout(args, config):
    if args.timeout is not None:
        return args.timeout
    return float((config.get("remote_terminal", {}) or {}).get("http_timeout", 10))


def post(url, endpoint, payload, timeout):
    req = urllib.request.Request(
        f"{url}{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            print(json.dumps(body))
            return body
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(json.dumps({"status": "error", "code": exc.code, "detail": detail}))
        raise SystemExit(1)
    except urllib.error.URLError as exc:
        print(json.dumps({"status": "error", "detail": str(exc.reason)}))
        raise SystemExit(1)


def action_execute(args, config):
    rt = config.get("remote_terminal", {}) or {}
    payload = {
        "actions": [
            {"action": "click", "args": [rt.get("click_x", 500), rt.get("click_y", 300)]},
            {"sleep": rt.get("focus_delay", 0.3)},
            {"action": "pyperclip.copy", "args": [args.command]},
            {"action": "hotkey", "args": ["ctrl", "shift", "v"]},
            {"sleep": 0.1},
            {"action": "press", "args": ["enter"]},
        ]
    }
    post(base_url(args, config), "/batch", payload, request_timeout(args, config))


def action_send_ctrlc(args, config):
    rt = config.get("remote_terminal", {}) or {}
    payload = {
        "actions": [
            {"action": "click", "args": [rt.get("click_x", 500), rt.get("click_y", 300)]},
            {"sleep": 0.2},
            {"action": "hotkey", "args": ["ctrl", "c"]},
        ]
    }
    post(base_url(args, config), "/batch", payload, request_timeout(args, config))


def action_click_reset_hand(args, config):
    rh = config.get("reset_hand", {}) or {}
    if "click_x" not in rh or "click_y" not in rh:
        print(json.dumps({"status": "error", "detail": "reset_hand.click_x/click_y missing"}))
        raise SystemExit(1)
    post(
        base_url(args, config),
        "/batch",
        {"actions": [{"action": "click", "args": [rh["click_x"], rh["click_y"]]}]},
        request_timeout(args, config),
    )


def action_calibrate(args, config):
    post(base_url(args, config), "/exec", {"action": "position"}, request_timeout(args, config))


def main():
    parser = argparse.ArgumentParser(description="Send commands to remote PyAutoGUI service.")
    parser.add_argument("--action", required=True, choices=["execute", "send_ctrlc", "click_reset_hand", "calibrate"])
    parser.add_argument("--command")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--host")
    parser.add_argument("--timeout", type=float)
    args = parser.parse_args()

    if args.action == "execute" and not args.command:
        parser.error("--command is required for execute")

    config = load_config(args.config)
    {
        "execute": action_execute,
        "send_ctrlc": action_send_ctrlc,
        "click_reset_hand": action_click_reset_hand,
        "calibrate": action_calibrate,
    }[args.action](args, config)


if __name__ == "__main__":
    main()
