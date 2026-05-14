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

from utils import load_config, loop_safety_limits

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
VENV_PYTHON = SKILL_DIR / ".venv" / "bin" / "python"
REEXEC_ENV = "DEXHOLDEM_V2_PREFLIGHT_REEXECED"
RUNTIME_FILES = [
    "utils.py",
    "capture.py",
    "state.py",
    "executor.py",
    "action_translator.py",
    "text_to_sound.py",
    "router.py",
    "remote_exec.py",
]
TTS_BACKEND_BINS = {
    "say_afplay": ["say", "afplay"],
    "say": ["say"],
    "spd-say": ["spd-say"],
    "espeak-ng": ["espeak-ng"],
    "espeak": ["espeak"],
}
TTS_AUTO_BACKENDS = ("say_afplay", "spd-say", "espeak-ng", "espeak")
TTS_APT_PACKAGES = {
    "spd-say": ["speech-dispatcher"],
    "espeak-ng": ["espeak-ng"],
    "espeak": ["espeak"],
}
TTS_APT_PACKAGE_ALIASES = {
    "auto": ["espeak-ng"],
    "speech-dispatcher": ["speech-dispatcher"],
    "spd-say": ["speech-dispatcher"],
    "espeak-ng": ["espeak-ng"],
    "espeak": ["espeak"],
}


def run_uv_sync(skip):
    if skip:
        return True, {"skipped": True}
    if shutil.which("uv") is None:
        return False, {"detail": "uv not found on PATH"}
    result = subprocess.run(["uv", "sync"], cwd=SKILL_DIR, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        return False, {"detail": "uv sync failed", "stderr": result.stderr[-1000:]}
    return True, {"stdout_tail": result.stdout[-500:], "stderr_tail": result.stderr[-500:]}


def available_backends(candidates):
    available = {}
    for candidate in candidates:
        bins = TTS_BACKEND_BINS[candidate]
        if all(shutil.which(name) for name in bins):
            available[candidate] = {name: shutil.which(name) for name in bins}
    return available


def text_to_sound_backend_available(config):
    tts = config.get("text_to_sound", {}) or {}
    if not tts.get("enabled", True):
        return True, {"backend": "none", "disabled": True}

    backend = tts.get("backend", "auto")
    if backend == "auto":
        available = available_backends(TTS_AUTO_BACKENDS)
        if available:
            return True, {"backend": backend, "available_backends": available}
        return False, {
            "detail": "text_to_sound auto backend found no supported local TTS command",
            "tried": {name: TTS_BACKEND_BINS[name] for name in TTS_AUTO_BACKENDS},
        }
    if backend in TTS_BACKEND_BINS:
        missing_bins = [name for name in TTS_BACKEND_BINS[backend] if shutil.which(name) is None]
        if missing_bins:
            return False, {"detail": "text_to_sound backend missing binaries", "missing": missing_bins}
        return True, {
            "backend": backend,
            "binaries": {name: shutil.which(name) for name in TTS_BACKEND_BINS[backend]},
        }
    if backend == "none":
        return True, {"backend": backend, "disabled": True}
    return False, {"detail": f"unknown text_to_sound backend: {backend}"}


def apt_packages_for_tts(config, package_choice):
    tts = config.get("text_to_sound", {}) or {}
    if not tts.get("enabled", True):
        return []
    if package_choice in TTS_APT_PACKAGE_ALIASES:
        return TTS_APT_PACKAGE_ALIASES[package_choice]
    backend = tts.get("backend", "auto")
    if backend == "auto":
        return TTS_APT_PACKAGE_ALIASES["auto"]
    return TTS_APT_PACKAGES.get(backend, [])


def run_apt_install(packages):
    if sys.platform != "linux":
        return False, {"detail": "system package installation is only supported on Linux", "platform": sys.platform}
    if not packages:
        return False, {"detail": "no apt packages are known for the configured text_to_sound backend"}
    if shutil.which("apt-get") is None:
        return False, {"detail": "apt-get not found; install the TTS package manually", "packages": packages}

    prefix = []
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        if shutil.which("sudo") is None:
            return False, {"detail": "sudo not found and current user is not root", "packages": packages}
        prefix = ["sudo", "-n"]

    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"
    commands = [
        prefix + ["apt-get", "update"],
        prefix + ["apt-get", "install", "-y", *packages],
    ]
    results = []
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
        item = {
            "command": cmd,
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-1000:],
            "stderr_tail": result.stderr[-1000:],
        }
        results.append(item)
        if result.returncode != 0:
            return False, {"packages": packages, "commands": results}
    return True, {"packages": packages, "commands": results}


def maybe_install_system_packages(config, skip_audio, install, tts_package):
    if skip_audio:
        return True, {"skipped": True, "reason": "audio checks skipped"}
    ok, detail = text_to_sound_backend_available(config)
    if ok:
        return True, {"skipped": True, "reason": "text_to_sound backend already available", "detail": detail}
    if not install:
        packages = apt_packages_for_tts(config, tts_package)
        return True, {
            "skipped": True,
            "reason": "pass --install-system-packages to install missing Linux TTS packages",
            "missing": detail,
            "suggested_apt_packages": packages,
        }
    packages = apt_packages_for_tts(config, tts_package)
    ok, install_detail = run_apt_install(packages)
    install_detail["initial_missing"] = detail
    return ok, install_detail


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


def post(base_url, endpoint, payload, timeout=10):
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
    timeout = float(rt.get("http_timeout", 10))
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
        hello = post(base, "/batch", hello_payload, timeout=timeout)
        reset = None
        if "click_x" in rh and "click_y" in rh:
            reset = post(base, "/batch", {
                "actions": [
                    {"action": "click", "args": [rh["click_x"], rh["click_y"]]},
                ]
            }, timeout=timeout)
        return True, {"type_hello_world": hello, "move_cursor_reset_hand": reset}
    except urllib.error.URLError as exc:
        return False, {"detail": str(exc.reason), "host": base}
    except Exception as exc:
        return False, {"detail": repr(exc), "host": base}


def check_audio(config, skip_audio):
    if skip_audio:
        return True, {"skipped": True}

    details = {}

    audio_config = config.get("audio", {}) or {}
    if audio_config.get("enabled", False):
        if shutil.which("ffplay") is None:
            return False, {"detail": "ffplay not found"}
        details["ffplay"] = shutil.which("ffplay")
        missing = []
        audio_dir = SKILL_DIR / "audio"
        for logical, filename in (audio_config.get("files", {}) or {}).items():
            if not (audio_dir / filename).exists():
                missing.append({"logical": logical, "filename": filename})
        if missing:
            return False, {"missing": missing}

    tts = config.get("text_to_sound", {}) or {}
    if tts.get("enabled", True):
        ok, tts_detail = text_to_sound_backend_available(config)
        if not ok:
            return False, tts_detail
        details["text_to_sound"] = tts_detail

    if not details:
        return True, {"skipped": True}

    return True, details


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_config(config, require_remote):
    errors = []
    rt = config.get("remote_terminal", {}) or {}
    rh = config.get("reset_hand", {}) or {}
    robot_client = config.get("robot_client", {}) or {}

    if require_remote and not rt.get("host"):
        errors.append("remote_terminal.host is required")

    for section_name, section, fields, required in (
        ("remote_terminal", rt, ("click_x", "click_y"), require_remote),
        ("reset_hand", rh, ("click_x", "click_y"), require_remote),
    ):
        for field in fields:
            value = section.get(field)
            if value is None:
                if required:
                    errors.append(f"{section_name}.{field} is required")
                continue
            if not _number(value) or value < 0:
                errors.append(f"{section_name}.{field} must be a non-negative number")

    timeout = rt.get("http_timeout", 10)
    if not _number(timeout) or timeout <= 0:
        errors.append("remote_terminal.http_timeout must be a positive number")

    if not isinstance(robot_client, dict):
        errors.append("robot_client must be a mapping")
        robot_client = {}

    port = robot_client.get("port", robot_client.get("default_port", 13579))
    if isinstance(port, bool) or not isinstance(port, int) or port <= 0:
        errors.append("robot_client.port must be a positive integer")

    instruction_ports = robot_client.get("instruction_ports", {}) or {}
    if not isinstance(instruction_ports, dict):
        errors.append("robot_client.instruction_ports must be a mapping")
    else:
        for key, value in instruction_ports.items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                errors.append(f"robot_client.instruction_ports.{key} must be a positive integer")

    try:
        safety_limits = loop_safety_limits(config)
    except Exception as exc:
        errors.append(str(exc))
        safety_limits = None

    if errors:
        return False, {"errors": errors}
    return True, {
        "remote_terminal": {
            "host": rt.get("host"),
            "click_x": rt.get("click_x"),
            "click_y": rt.get("click_y"),
            "http_timeout": timeout,
        },
        "reset_hand": {"click_x": rh.get("click_x"), "click_y": rh.get("click_y")},
        "robot_client": {
            "server_ip": robot_client.get("server_ip", "192.168.1.200"),
            "port": port,
            "instruction_ports": instruction_ports,
        },
        "loop_safety": safety_limits,
    }


def main():
    parser = argparse.ArgumentParser(description="Run DexHoldem V2 preflight.")
    parser.add_argument("--exp-name")
    parser.add_argument("--config", default=str(SKILL_DIR / "config.yaml"))
    parser.add_argument("--skip-uv-sync", action="store_true")
    parser.add_argument("--skip-camera", action="store_true")
    parser.add_argument("--skip-remote", action="store_true")
    parser.add_argument("--skip-audio", action="store_true")
    parser.add_argument("--install-system-packages", action="store_true", help="Install missing Linux TTS packages with apt-get")
    parser.add_argument(
        "--tts-package",
        default="auto",
        choices=sorted(TTS_APT_PACKAGE_ALIASES),
        help="apt package choice for --install-system-packages; auto installs espeak-ng",
    )
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

    try:
        config = load_config(args.config)
    except Exception as exc:
        record("config", False, {"detail": str(exc)})
        results["status"] = "failed"
        print(json.dumps(results, indent=2))
        raise SystemExit(1)
    ok, detail = validate_config(config, require_remote=not args.skip_remote)
    if not record("config", ok, detail):
        results["status"] = "failed"
        print(json.dumps(results, indent=2))
        raise SystemExit(1)

    ok, detail = maybe_install_system_packages(
        config,
        skip_audio=args.skip_audio,
        install=args.install_system_packages,
        tts_package=args.tts_package,
    )
    if not record("system_packages", ok, detail):
        results["status"] = "failed"
        print(json.dumps(results, indent=2))
        raise SystemExit(1)

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
