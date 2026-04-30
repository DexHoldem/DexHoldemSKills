#!/usr/bin/env python3
"""Preflight for DexHoldem V2."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
VENV_PYTHON = SKILL_DIR / ".venv" / "bin" / "python"
REEXEC_ENV = "DEXHOLDEM_V2_PREFLIGHT_REEXECED"
RUNTIME_FILES = [
    "capture.py",
    "state.py",
    "executor.py",
    "action_translator.py",
    "router.py",
    "workflow.py",
    "remote_exec.py",
]


def load_config(path):
    if not Path(path).exists():
        return {}
    try:
        import yaml
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {}


def run_uv_sync(skip):
    if skip:
        return True, {"skipped": True}
    if shutil.which("uv") is None:
        return False, {"detail": "uv not found on PATH"}
    result = subprocess.run(["uv", "sync"], cwd=SKILL_DIR, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        return False, {"detail": "uv sync failed", "stderr": result.stderr[-1000:]}
    return True, {"stdout_tail": result.stdout[-500:], "stderr_tail": result.stderr[-500:]}


def deps_importable():
    try:
        import yaml  # noqa: F401
        return True
    except ImportError:
        return False


def maybe_reexec(argv):
    if deps_importable() or os.environ.get(REEXEC_ENV) or not VENV_PYTHON.exists():
        return
    os.environ[REEXEC_ENV] = "1"
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), *argv])


def run_state_init(config_path, exp_name):
    args = [sys.executable, str(SCRIPT_DIR / "state.py"), "init-experiment", "--config", str(config_path)]
    if exp_name:
        args += ["--exp-name", exp_name]
    result = subprocess.run(args, capture_output=True, text=True, cwd=Path.cwd())
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)


def copy_runtime(exp_dir):
    exp_dir = Path(exp_dir)
    for name in RUNTIME_FILES:
        dest = exp_dir / name
        shutil.copy2(SCRIPT_DIR / name, dest)
        dest.chmod(0o755)
    shutil.copy2(SKILL_DIR / "pyproject.toml", exp_dir / "pyproject.toml")
    shutil.copy2(SKILL_DIR / "config.yaml", exp_dir / "config.yaml")
    visual_dest = exp_dir / "visual_guidelines"
    if visual_dest.exists():
        shutil.rmtree(visual_dest)
    shutil.copytree(SKILL_DIR / "visual_guidelines", visual_dest)


def capture_initial(exp_dir, skip_camera, source=None):
    if skip_camera:
        return True, {"skipped": True}
    output = Path(exp_dir) / "s0" / "00_capture.jpg"
    cmd = [sys.executable, str(Path(exp_dir) / "capture.py"), "--output", str(output), "--meta"]
    if source:
        cmd += ["--source", source]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=exp_dir, timeout=30)
    if result.returncode != 0:
        return False, {"stderr": result.stderr.strip(), "stdout": result.stdout.strip()}
    return True, {"output": str(output)}


def post(base_url, endpoint, payload, timeout=5):
    req = urllib.request.Request(
        f"{base_url}{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check_remote(config, skip_remote):
    if skip_remote:
        return True, {"skipped": True}
    rt = config.get("remote_terminal", {}) or {}
    rh = config.get("reset_hand", {}) or {}
    base = rt.get("host", "http://localhost:5000").rstrip("/")
    try:
        hello_payload = {
            "actions": [
                {"action": "click", "args": [rt.get("click_x", 500), rt.get("click_y", 300)]},
                {"sleep": rt.get("focus_delay", 0.3)},
                {"action": "pyperclip.copy", "args": ["echo hello world"]},
                {"action": "hotkey", "args": ["ctrl", "shift", "v"]},
                {"sleep": 0.1},
                {"action": "press", "args": ["enter"]},
            ]
        }
        hello = post(base, "/batch", hello_payload)
        reset = None
        if "click_x" in rh and "click_y" in rh:
            reset = post(base, "/batch", {
                "actions": [
                    {"action": "moveTo", "args": [rh["click_x"], rh["click_y"]], "kwargs": {"duration": 0.3}},
                ]
            })
        return True, {"type_hello_world": hello, "move_cursor_reset_hand": reset}
    except urllib.error.URLError as exc:
        return False, {"detail": str(exc.reason), "host": base}
    except Exception as exc:
        return False, {"detail": repr(exc), "host": base}


def check_audio(config, skip_audio):
    if skip_audio or not (config.get("audio", {}) or {}).get("enabled", False):
        return True, {"skipped": True}
    if shutil.which("ffplay") is None:
        return False, {"detail": "ffplay not found"}
    missing = []
    audio_dir = SKILL_DIR / "audio"
    for logical, filename in ((config.get("audio", {}) or {}).get("files", {}) or {}).items():
        if not (audio_dir / filename).exists():
            missing.append({"logical": logical, "filename": filename})
    if missing:
        return False, {"missing": missing}
    return True, {"ffplay": shutil.which("ffplay")}


def main():
    parser = argparse.ArgumentParser(description="Run DexHoldem V2 preflight.")
    parser.add_argument("--exp-name")
    parser.add_argument("--config", default=str(SKILL_DIR / "config.yaml"))
    parser.add_argument("--skip-uv-sync", action="store_true")
    parser.add_argument("--skip-camera", action="store_true")
    parser.add_argument("--skip-remote", action="store_true")
    parser.add_argument("--skip-audio", action="store_true")
    parser.add_argument("--camera-source", help="Copy an existing image as s0/00_capture.jpg")
    args = parser.parse_args()

    results = {"checks": []}

    def record(name, ok, detail):
        results["checks"].append({"name": name, "ok": ok, "detail": detail})
        return ok

    ok, detail = run_uv_sync(args.skip_uv_sync)
    if not record("uv_sync", ok, detail):
        results["status"] = "failed"
        print(json.dumps(results, indent=2))
        raise SystemExit(1)
    maybe_reexec(sys.argv)

    config = load_config(args.config)

    try:
        init = run_state_init(args.config, args.exp_name)
        exp_dir = Path(init["exp_dir"])
        record("experiment_dir", True, init)
    except Exception as exc:
        record("experiment_dir", False, {"detail": str(exc)})
        results["status"] = "failed"
        print(json.dumps(results, indent=2))
        raise SystemExit(1)

    try:
        copy_runtime(exp_dir)
        record("runtime_copy", True, {"files": RUNTIME_FILES, "exp_dir": str(exp_dir)})
    except Exception as exc:
        record("runtime_copy", False, {"detail": str(exc)})
        results["status"] = "failed"
        print(json.dumps(results, indent=2))
        raise SystemExit(1)

    ok, detail = capture_initial(exp_dir, args.skip_camera, args.camera_source)
    if not record("camera", ok, detail):
        results["status"] = "failed"
        print(json.dumps(results, indent=2))
        raise SystemExit(1)

    ok, detail = check_remote(config, args.skip_remote)
    if not record("remote", ok, detail):
        results["status"] = "failed"
        print(json.dumps(results, indent=2))
        raise SystemExit(1)

    ok, detail = check_audio(config, args.skip_audio)
    if not record("audio", ok, detail):
        results["status"] = "failed"
        print(json.dumps(results, indent=2))
        raise SystemExit(1)

    results["status"] = "ok"
    results["experiment"] = {"exp_dir": str(exp_dir), "current": str(exp_dir.parent / "current")}
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
