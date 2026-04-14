#!/usr/bin/env python3
"""Preflight check for the DexHoldem loop.

Verifies everything the main loop depends on before the first iteration:
    1. remote_terminal.host is reachable (calls /exec `position`).
    2. Paste-and-run of `echo hello world` works via the same path executor uses.
    3. Local camera can capture a non-empty frame.
    4. An experiment directory exists to receive state/frames for this session.

Exit code 0 on success, 1 on failure. JSON result printed to stdout.

Usage:
    python3 src/preflight.py
    python3 src/preflight.py --exp-name friday_night
    python3 src/preflight.py --host http://192.168.1.201:5000 --camera-device 0
    python3 src/preflight.py --skip-camera
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime

import yaml

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SRC_DIR)


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


# ── check: remote connection ──────────────────────────────────────────────

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


# ── check: paste-and-run hello world ──────────────────────────────────────

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


# ── check: camera ─────────────────────────────────────────────────────────

def check_camera(device, output_path):
    """Run capture.py and verify a non-empty image was written."""
    cmd = [
        sys.executable,
        os.path.join(SRC_DIR, "capture.py"),
        "--device", str(device),
        "--output", output_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        return False, {"detail": "capture.py timed out after 15s"}
    except Exception as e:
        return False, {"detail": repr(e)}

    if result.returncode != 0:
        return False, {
            "detail": "capture.py exited non-zero",
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }

    if not os.path.exists(output_path):
        return False, {"detail": f"output file not created: {output_path}"}

    size = os.path.getsize(output_path)
    if size == 0:
        return False, {"detail": f"output file is empty: {output_path}"}

    return True, {"output_path": output_path, "size_bytes": size, "device": device}


# ── check: experiment directory ───────────────────────────────────────────

def _base_dir(config):
    rel = config.get("experiments", {}).get("base_dir", "./experiments")
    if os.path.isabs(rel):
        return rel
    return os.path.join(SKILL_DIR, rel)


def ensure_experiment_dir(config, exp_name=None):
    """Create experiments/<name>/ and point `current` symlink at it.

    If exp_name is None, a timestamped default is used: exp{YYYYMMDD}_{HHMMSS}.
    Returns (ok, detail).
    """
    base = _base_dir(config)
    try:
        os.makedirs(base, exist_ok=True)
    except Exception as e:
        return False, {"detail": f"cannot create base dir {base}: {e}"}

    if not exp_name:
        exp_name = datetime.now().strftime("exp%Y%m%d_%H%M%S")

    exp_dir = os.path.join(base, exp_name)
    frames_dir = os.path.join(exp_dir, "frames")

    try:
        os.makedirs(frames_dir, exist_ok=True)
    except Exception as e:
        return False, {"detail": f"cannot create {frames_dir}: {e}"}

    # update 'current' symlink to point at this experiment
    link = os.path.join(base, "current")
    try:
        if os.path.islink(link) or os.path.exists(link):
            if os.path.islink(link):
                os.remove(link)
            else:
                return False, {"detail": f"{link} exists and is not a symlink"}
        os.symlink(exp_dir, link)
    except Exception as e:
        return False, {"detail": f"cannot update current symlink: {e}"}

    return True, {
        "exp_name": exp_name,
        "exp_dir": exp_dir,
        "frames_dir": frames_dir,
        "current_symlink": link,
    }


# ── main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Preflight check for the DexHoldem loop.")
    parser.add_argument(
        "--config",
        default=os.path.join(SKILL_DIR, "config.yaml"),
        help="Path to config.yaml",
    )
    parser.add_argument("--host", help="Override remote service URL")
    parser.add_argument(
        "--exp-name",
        default=None,
        help="Experiment directory name (default: exp{YYYYMMDD}_{HHMMSS})",
    )
    parser.add_argument(
        "--camera-device", type=int, default=0,
        help="Camera device index passed to capture.py (default: 0)",
    )
    parser.add_argument(
        "--camera-output",
        default="/tmp/poker_preflight.jpg",
        help="Where the preflight test frame is written",
    )
    parser.add_argument("--skip-camera", action="store_true", help="Skip the camera check")
    parser.add_argument("--skip-remote", action="store_true", help="Skip remote terminal checks")
    args = parser.parse_args()

    config = _load_config(args.config)
    rt = config.get("remote_terminal", {}) or {}
    base_url = (args.host or rt.get("host", "http://localhost:5000")).rstrip("/")

    results = {"host": base_url, "checks": []}

    def record(name, ok, detail):
        results["checks"].append({"name": name, "ok": ok, "detail": detail})
        return ok

    def fail(err):
        results["status"] = "failed"
        results["error"] = err
        print(json.dumps(results, indent=2))
        sys.exit(1)

    # 1. remote connection
    if args.skip_remote:
        record("connection", True, {"skipped": True})
    else:
        ok, detail = check_connection(base_url)
        if not record("connection", ok, detail):
            fail("cannot reach remote_terminal.host")

    # 2. paste-and-run hello world
    if args.skip_remote:
        record("type_hello_world", True, {"skipped": True})
    else:
        ok, detail = check_type_hello_world(base_url, rt)
        if not record("type_hello_world", ok, detail):
            fail("paste-to-terminal failed")

    # 3. camera
    if args.skip_camera:
        record("camera", True, {"skipped": True})
    else:
        ok, detail = check_camera(args.camera_device, args.camera_output)
        if not record("camera", ok, detail):
            fail("camera capture failed")

    # 4. experiment directory
    ok, detail = ensure_experiment_dir(config, exp_name=args.exp_name)
    if not record("experiment_dir", ok, detail):
        fail("could not create experiment directory")

    results["status"] = "ok"
    results["experiment"] = detail
    print(json.dumps(results, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
