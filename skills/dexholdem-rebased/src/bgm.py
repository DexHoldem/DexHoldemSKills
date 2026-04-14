#!/usr/bin/env python3
"""BGM + SFX manager for the dexholdem loop.

BGM is a looping background track (one at a time) played via a tiny
Python supervisor that restarts ffplay until killed. SFX are one-shot
ffplay spawns that do not touch BGM state. All audio plays locally on
the agent machine (same machine as this script).

Subcommands:
    bgm.py loop <file> [--only-if-silent]
        Start or replace BGM. Idempotent: if already looping the same
        file, no-op. With --only-if-silent, no-op if *any* BGM is live.

    bgm.py stop
        Kill the BGM supervisor (and its ffplay child), clear state.

    bgm.py oneshot <file>
        Stop BGM, then spawn a detached fire-and-forget ffplay. Leaves
        BGM stopped.

    bgm.py sfx <file> [--chance F]
        Fire-and-forget ffplay. Does not touch BGM state. If --chance
        is given, rolls random() < F first and no-ops on failure.

    bgm.py status
        Print the BGM state file contents (or {} when silent).

    bgm.py _daemon --file <abs-path>
        Internal supervisor: `while True: subprocess.run(ffplay ...)`.
        Not meant to be invoked directly.

File resolution: the `<file>` positional can be a logical name declared
in config.yaml under `audio.files` (e.g. "start", "allin", "view_card")
or a literal filename in the audio/ directory. Logical names win if
both resolve.

State file: <current_exp>/bgm_state.json, or /tmp/dexholdem_bgm.json
when no experiment is active. Contains {"pgid", "file", "mode"}.
"""

import argparse
import json
import os
import random
import signal
import subprocess
import sys
import time

try:
    import yaml
except ImportError:
    yaml = None


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(SKILL_DIR, "audio")
CONFIG_PATH = os.path.join(SKILL_DIR, "config.yaml")
FALLBACK_STATE = "/tmp/dexholdem_bgm.json"


# ── config / paths ─────────────────────────────────────────────────────────

def _load_config():
    if yaml is None or not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f) or {}


def _audio_cfg(config):
    return config.get("audio", {}) or {}


def _audio_enabled(config):
    return bool(_audio_cfg(config).get("enabled", True))


def _current_exp_dir(config):
    """Resolve <base_dir>/current if it exists, else None."""
    rel = config.get("experiments", {}).get("base_dir", "./experiments")
    base = rel if os.path.isabs(rel) else os.path.join(os.getcwd(), rel)
    link = os.path.join(base, "current")
    if os.path.islink(link) or os.path.isdir(link):
        return os.path.realpath(link)
    return None


def _state_path(config):
    exp = _current_exp_dir(config)
    if exp:
        return os.path.join(exp, "bgm_state.json")
    return FALLBACK_STATE


def _resolve_file(name, config):
    """Map a logical name (e.g. "start") or bare filename to an absolute path."""
    mapping = _audio_cfg(config).get("files", {}) or {}
    filename = mapping.get(name, name)
    return os.path.join(AUDIO_DIR, filename)


# ── state file ────────────────────────────────────────────────────────────

def _load_state(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_state(path, state):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, path)


def _clear_state(path):
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def _pgid_alive(pgid):
    if not pgid:
        return False
    try:
        os.killpg(pgid, 0)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


# ── ffplay helpers ────────────────────────────────────────────────────────

FFPLAY_FLAGS = ["-nodisp", "-autoexit", "-loglevel", "quiet"]


def _spawn_oneshot(abs_path):
    """Fire-and-forget ffplay in its own session; return the child PID."""
    cmd = ["ffplay", *FFPLAY_FLAGS, abs_path]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return proc.pid


def _spawn_daemon(abs_path):
    """Spawn `bgm.py _daemon --file <abs_path>` as a detached process group.
    Returns the process group id.
    """
    cmd = [sys.executable, os.path.abspath(__file__), "_daemon", "--file", abs_path]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,  # setsid → new session + pgid == pid
    )
    return os.getpgid(proc.pid)


def _kill_pgid(pgid):
    if not pgid:
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except OSError:
        return
    # Give it a moment to exit cleanly, then escalate.
    for _ in range(10):
        if not _pgid_alive(pgid):
            return
        time.sleep(0.05)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, OSError):
        pass


# ── subcommands ───────────────────────────────────────────────────────────

def cmd_loop(args, config):
    if not _audio_enabled(config):
        return
    state_path = _state_path(config)
    state = _load_state(state_path)
    abs_path = _resolve_file(args.file, config)
    if not os.path.isfile(abs_path):
        print(f"Error: audio file not found: {abs_path}", file=sys.stderr)
        sys.exit(1)

    cur_pgid = state.get("pgid")
    cur_file = state.get("file")
    cur_alive = _pgid_alive(cur_pgid)

    # --only-if-silent: any live BGM blocks the request.
    if args.only_if_silent and cur_alive:
        return

    # Idempotent: same file and still alive → no-op.
    if cur_alive and cur_file == os.path.basename(abs_path):
        return

    # Replace: kill previous supervisor (if any) then spawn.
    if cur_alive:
        _kill_pgid(cur_pgid)

    pgid = _spawn_daemon(abs_path)
    _save_state(state_path, {
        "pgid": pgid,
        "file": os.path.basename(abs_path),
        "mode": "loop",
    })


def cmd_stop(args, config):
    if not _audio_enabled(config):
        return
    state_path = _state_path(config)
    state = _load_state(state_path)
    pgid = state.get("pgid")
    if pgid:
        _kill_pgid(pgid)
    _clear_state(state_path)


def cmd_oneshot(args, config):
    if not _audio_enabled(config):
        return
    abs_path = _resolve_file(args.file, config)
    if not os.path.isfile(abs_path):
        print(f"Error: audio file not found: {abs_path}", file=sys.stderr)
        sys.exit(1)
    # Stop BGM first so the oneshot plays cleanly.
    cmd_stop(args, config)
    _spawn_oneshot(abs_path)


def cmd_sfx(args, config):
    if not _audio_enabled(config):
        return
    if args.chance is not None and random.random() >= args.chance:
        return
    abs_path = _resolve_file(args.file, config)
    if not os.path.isfile(abs_path):
        print(f"Error: audio file not found: {abs_path}", file=sys.stderr)
        sys.exit(1)
    _spawn_oneshot(abs_path)


def cmd_status(args, config):
    state_path = _state_path(config)
    state = _load_state(state_path)
    if state and not _pgid_alive(state.get("pgid")):
        # Stale state file from a crashed daemon — report empty.
        state = {}
    print(json.dumps(state, indent=2))


def cmd_daemon(args, config):
    """Supervisor: loop ffplay until SIGTERM."""
    stop_flag = {"stop": False}
    current = {"proc": None}

    def _handler(signum, frame):
        stop_flag["stop"] = True
        p = current["proc"]
        if p and p.poll() is None:
            try:
                p.terminate()
            except OSError:
                pass

    signal.signal(signal.SIGTERM, _handler)
    signal.signal(signal.SIGINT, _handler)

    while not stop_flag["stop"]:
        proc = subprocess.Popen(
            ["ffplay", *FFPLAY_FLAGS, args.file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        current["proc"] = proc
        try:
            proc.wait()
        except KeyboardInterrupt:
            stop_flag["stop"] = True
            try:
                proc.terminate()
            except OSError:
                pass
            break
        if stop_flag["stop"]:
            break
        # If ffplay exited abnormally (e.g. audio device gone), brief backoff.
        if proc.returncode != 0:
            time.sleep(0.5)


# ── main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="BGM + SFX manager (ffplay-based).")
    sub = parser.add_subparsers(dest="command", required=True)

    p_loop = sub.add_parser("loop", help="Start or replace BGM loop")
    p_loop.add_argument("file", help="Logical name or audio filename")
    p_loop.add_argument("--only-if-silent", action="store_true",
                        help="No-op if any BGM is already playing")

    sub.add_parser("stop", help="Stop BGM")

    p_one = sub.add_parser("oneshot", help="Stop BGM, play file once")
    p_one.add_argument("file", help="Logical name or audio filename")

    p_sfx = sub.add_parser("sfx", help="Fire-and-forget SFX (does not touch BGM)")
    p_sfx.add_argument("file", help="Logical name or audio filename")
    p_sfx.add_argument("--chance", type=float, default=None,
                       help="Probability (0-1) of actually playing")

    sub.add_parser("status", help="Print BGM state")

    p_d = sub.add_parser("_daemon", help=argparse.SUPPRESS)
    p_d.add_argument("--file", required=True, help="Absolute path to audio file")

    args = parser.parse_args()
    config = _load_config()

    {
        "loop": cmd_loop,
        "stop": cmd_stop,
        "oneshot": cmd_oneshot,
        "sfx": cmd_sfx,
        "status": cmd_status,
        "_daemon": cmd_daemon,
    }[args.command](args, config)


if __name__ == "__main__":
    main()
