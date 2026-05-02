#!/usr/bin/env python3
"""Speak short action phrases for DexHoldem V2."""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from utils import load_config


DEFAULT_ACTION_TEXT = {
    "check": "Check",
    "request_human": "Human help required",
}


def load_text_to_sound_config(config_path):
    try:
        return load_config(config_path), None
    except RuntimeError as exc:
        if "PyYAML is required" in str(exc):
            return {}, str(exc)
        raise


def _truthy(value, default=False):
    if value is None:
        return default
    return bool(value)


def resolve_text(action, text, config):
    if text:
        return text
    actions = (config.get("actions", {}) or {}) if isinstance(config, dict) else {}
    if action and actions.get(action):
        return str(actions[action])
    if action and DEFAULT_ACTION_TEXT.get(action):
        return DEFAULT_ACTION_TEXT[action]
    if action:
        return action.replace("_", " ")
    raise ValueError("--text is required when --action is omitted")


def backend_commands(backend, text, config):
    backend = backend or "auto"
    voice = config.get("voice")
    rate = config.get("rate")
    volume = config.get("volume", 1)

    if backend == "none":
        return None, "backend disabled"

    if backend in ("auto", "say_afplay") and shutil.which("say") and shutil.which("afplay"):
        return {"backend": "say_afplay", "volume": str(volume)}, None

    if backend == "say_afplay":
        return None, "say_afplay backend requires both say and afplay"

    if backend == "say" and shutil.which("say"):
        cmd = ["say"]
        if voice:
            cmd += ["-v", str(voice)]
        if rate:
            cmd += ["-r", str(int(rate))]
        cmd.append(text)
        return [cmd], None

    if backend in ("auto", "spd-say") and shutil.which("spd-say"):
        cmd = ["spd-say", "--wait"]
        if config.get("spd_rate") is not None:
            cmd += ["--rate", str(int(config["spd_rate"]))]
        cmd.append(text)
        return [cmd], None

    if backend == "spd-say":
        return None, "spd-say backend requires spd-say"

    if backend in ("auto", "espeak-ng") and shutil.which("espeak-ng"):
        cmd = ["espeak-ng"]
        if voice:
            cmd += ["-v", str(voice)]
        if rate:
            cmd += ["-s", str(int(rate))]
        cmd.append(text)
        return [cmd], None

    if backend == "espeak-ng":
        return None, "espeak-ng backend requires espeak-ng"

    if backend in ("auto", "espeak") and shutil.which("espeak"):
        cmd = ["espeak"]
        if voice:
            cmd += ["-v", str(voice)]
        if rate:
            cmd += ["-s", str(int(rate))]
        cmd.append(text)
        return [cmd], None

    if backend == "espeak":
        return None, "espeak backend requires espeak"

    if backend == "auto":
        return None, "no supported local text-to-speech backend found; tried say_afplay, spd-say, espeak-ng, and espeak"
    return None, f"configured text-to-speech backend is unavailable: {backend}"


def build_say_command(output_path, text, config):
    cmd = ["say", "-o", str(output_path)]
    if config.get("voice"):
        cmd += ["-v", str(config["voice"])]
    if config.get("rate"):
        cmd += ["-r", str(int(config["rate"]))]
    cmd.append(text)
    return cmd


def run_command(cmd, timeout):
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    result = {"command": cmd, "returncode": completed.returncode}
    if completed.stdout:
        result["stdout"] = completed.stdout[-500:]
    if completed.stderr:
        result["stderr"] = completed.stderr[-500:]
    return result


def play_say_afplay(text, config, timeout, dry_run):
    suffix = ".aiff"
    display_path = "/tmp/dexholdem_text_to_sound_preview.aiff"
    say_cmd = build_say_command(display_path, text, config)
    afplay_cmd = ["afplay", "-v", str(config.get("volume", 1)), display_path]
    if dry_run:
        return {
            "status": "dry_run",
            "backend_resolved": "say_afplay",
            "commands": [say_cmd, afplay_cmd],
        }

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        output_path = Path(f.name)
    try:
        say_cmd = build_say_command(output_path, text, config)
        say_result = run_command(say_cmd, timeout)
        if say_result["returncode"] != 0:
            return {
                "status": "failed",
                "backend_resolved": "say_afplay",
                "step": "say",
                "command_results": [say_result],
                "reason": say_result.get("stderr") or say_result.get("stdout") or "say failed to synthesize audio",
            }
        afplay_cmd = ["afplay", "-v", str(config.get("volume", 1)), str(output_path)]
        afplay_result = run_command(afplay_cmd, timeout)
        if afplay_result["returncode"] != 0:
            return {
                "status": "failed",
                "backend_resolved": "say_afplay",
                "step": "afplay",
                "command_results": [say_result, afplay_result],
                "reason": afplay_result.get("stderr") or afplay_result.get("stdout") or "afplay failed to play audio",
            }
        return {
            "status": "spoken",
            "backend_resolved": "say_afplay",
            "command_results": [say_result, afplay_result],
        }
    finally:
        output_path.unlink(missing_ok=True)


def speak(action=None, text=None, dry_run=False, config_path="config.yaml", required=None):
    full_config, config_warning = load_text_to_sound_config(config_path)
    config = full_config.get("text_to_sound", {}) or {}
    enabled = _truthy(config.get("enabled"), True)
    required = _truthy(config.get("required"), False) if required is None else required
    phrase = resolve_text(action, text, config)
    backend = config.get("backend", "auto")
    timeout = float(config.get("timeout", 5))

    result = {
        "status": "pending",
        "action": action,
        "text": phrase,
        "backend": backend,
        "dry_run": dry_run,
        "required": required,
    }
    if config_warning:
        result["config_warning"] = config_warning

    if not enabled:
        result.update({"status": "skipped", "reason": "text_to_sound disabled"})
        return result, 0

    commands, reason = backend_commands(backend, phrase, config)
    if commands is None:
        result.update({"status": "failed" if required else "skipped", "reason": reason})
        return result, 1 if required else 0

    if isinstance(commands, dict) and commands.get("backend") == "say_afplay":
        playback = play_say_afplay(phrase, config, timeout, dry_run)
        result.update(playback)
        if playback["status"] in ("spoken", "dry_run"):
            return result, 0
        return result, 1 if required else 0

    result["commands"] = commands
    if dry_run:
        result.update({"status": "dry_run", "backend_resolved": backend})
        return result, 0

    command_results = []
    try:
        for cmd in commands:
            command_results.append(run_command(cmd, timeout))
    except Exception as exc:
        result.update({"status": "failed", "reason": str(exc)})
        return result, 1 if required else 0

    result["command_results"] = command_results
    failed = [item for item in command_results if item["returncode"] != 0]
    if not failed:
        result.update({"status": "spoken", "backend_resolved": backend})
        return result, 0
    result["status"] = "failed"
    result["reason"] = failed[0].get("stderr") or failed[0].get("stdout") or "text-to-speech command failed"
    return result, 1 if required else 0


def main():
    parser = argparse.ArgumentParser(description="Speak a short DexHoldem action phrase.")
    parser.add_argument("--action", help="Action name, for example check")
    parser.add_argument("--text", help="Override spoken text")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--required", action="store_true", help="Return non-zero when speech cannot be produced")
    args = parser.parse_args()

    result, code = speak(
        action=args.action,
        text=args.text,
        dry_run=args.dry_run,
        config_path=args.config,
        required=True if args.required else None,
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
