#!/usr/bin/env python3
"""Preflight check for the DexHoldem loop.

Verifies that the remote PyAutoGUI terminal service is reachable and that
paste-into-terminal works end-to-end. Run this before starting the main loop.

Checks:
    1. HTTP reachability of remote_terminal.host (calls /exec with `position`).
    2. Paste-and-run a harmless `echo hello world` into the remote terminal
       via the same code path the executor uses.

Exit code 0 on success, 1 on failure. JSON result printed to stdout.

Usage:
    python3 src/preflight.py
    python3 src/preflight.py --host http://192.168.1.201:5000
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

import yaml

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_config(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def _post(base_url, endpoint, payload, timeout=5.0):
    url = f"{base_url}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check_connection(base_url):
    """Ping the remote service via /exec position."""
    try:
        body = _post(base_url, "/exec", {"action": "position"})
        return True, body
    except urllib.error.HTTPError as e:
        return False, {"code": e.code, "detail": e.read().decode("utf-8", errors="replace")}
    except urllib.error.URLError as e:
        return False, {"detail": str(e.reason)}
    except Exception as e:
        return False, {"detail": repr(e)}


def check_type_hello_world(base_url, rt):
    """Focus the remote terminal and paste+run `echo hello world`."""
    click_x = rt.get("click_x", 500)
    click_y = rt.get("click_y", 300)
    focus_delay = rt.get("focus_delay", 0.3)
    payload = {
        "actions": [
            {"action": "click", "args": [click_x, click_y]},
            {"sleep": focus_delay},
            {"action": "pyperclip.copy", "args": ["echo hello world"]},
            {"action": "hotkey", "args": ["ctrl", "shift", "v"]},
            {"sleep": 0.1},
            {"action": "press", "args": ["enter"]},
        ]
    }
    try:
        body = _post(base_url, "/batch", payload)
        return True, body
    except urllib.error.HTTPError as e:
        return False, {"code": e.code, "detail": e.read().decode("utf-8", errors="replace")}
    except urllib.error.URLError as e:
        return False, {"detail": str(e.reason)}
    except Exception as e:
        return False, {"detail": repr(e)}


def main():
    parser = argparse.ArgumentParser(description="Preflight check for DexHoldem remote terminal.")
    parser.add_argument(
        "--config",
        default=os.path.join(SKILL_DIR, "config.yaml"),
        help="Path to config.yaml",
    )
    parser.add_argument("--host", help="Override remote service URL")
    args = parser.parse_args()

    config = _load_config(args.config)
    rt = config.get("remote_terminal", {}) or {}
    base_url = (args.host or rt.get("host", "http://localhost:5000")).rstrip("/")

    results = {"host": base_url, "checks": []}

    ok, detail = check_connection(base_url)
    results["checks"].append({"name": "connection", "ok": ok, "detail": detail})
    if not ok:
        results["status"] = "failed"
        results["error"] = "cannot reach remote_terminal.host"
        print(json.dumps(results, indent=2))
        sys.exit(1)

    ok, detail = check_type_hello_world(base_url, rt)
    results["checks"].append({"name": "type_hello_world", "ok": ok, "detail": detail})
    if not ok:
        results["status"] = "failed"
        results["error"] = "paste-to-terminal failed"
        print(json.dumps(results, indent=2))
        sys.exit(1)

    results["status"] = "ok"
    print(json.dumps(results, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
