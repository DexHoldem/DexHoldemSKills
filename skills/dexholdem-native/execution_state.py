#!/usr/bin/env python3
"""Execution state tracker with experiment directory management.

Creates per-session experiment folders (./experiments/exp{date}_{seq}/) that
store execution state, captured frames, and game logs. A symlink
./experiments/current always points to the active experiment.

Subcommands:
    init         Create a new experiment directory, print its path
    save         Write execution state
    update       Update fields in existing state
    load         Print current state JSON to stdout (exit 1 if none)
    clear        Remove state file (keep experiment dir + frames)
    save-frame   Copy a captured frame into the experiment's frames/ dir

State file schema:
    {
        "phase": "idle|recognizing|deciding|executing|verifying",
        "round": 5,
        "current_action": {"action": "call", "bet_chips": 50},
        "command_sequence": ["pick_chips", "place_bet"],
        "commands_completed": 0,
        "last_verified_frame": "frames/r005_002_stable.jpg",
        "timestamp": "2026-03-19T14:30:00Z"
    }
"""

import argparse
import glob
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

import yaml

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_config():
    config_path = os.path.join(SKILL_DIR, "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def _base_dir(config):
    rel = config.get("experiments", {}).get("base_dir", "./experiments")
    if os.path.isabs(rel):
        return rel
    return os.path.join(os.getcwd(), rel)


def _current_exp_dir(config):
    """Resolve the active experiment dir via the 'current' symlink."""
    base = _base_dir(config)
    link = os.path.join(base, "current")
    if os.path.islink(link) or os.path.isdir(link):
        return os.path.realpath(link)
    return None


def _state_path_for(exp_dir):
    return os.path.join(exp_dir, "state.json")


def _default_state_path(config):
    exp_dir = _current_exp_dir(config)
    if exp_dir:
        return _state_path_for(exp_dir)
    return None


# ── state I/O ──────────────────────────────────────────────────────────────

def load_state(state_path):
    if not state_path or not os.path.exists(state_path):
        return None
    with open(state_path, "r") as f:
        return json.load(f)


def save_state(state_path, state):
    state["timestamp"] = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    tmp = state_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, state_path)


def clear_state(state_path):
    if state_path and os.path.exists(state_path):
        os.remove(state_path)


# ── hand cache ────────────────────────────────────────────────────────────

def _hand_cache_path(config):
    exp_dir = _current_exp_dir(config)
    if exp_dir:
        return os.path.join(exp_dir, "hand_cache.json")
    return None


def load_hand_cache(cache_path):
    if not cache_path or not os.path.exists(cache_path):
        return {"left": None, "right": None}
    with open(cache_path, "r") as f:
        return json.load(f)


def save_hand_cache(cache_path, cache):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    tmp = cache_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cache, f, indent=2)
    os.replace(tmp, cache_path)


# ── init ───────────────────────────────────────────────────────────────────

def cmd_init(args, config):
    base = _base_dir(config)
    os.makedirs(base, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    prefix = f"exp{today}_"

    # find next sequence number
    existing = glob.glob(os.path.join(base, f"{prefix}*"))
    seq_nums = []
    for p in existing:
        m = re.search(rf"{prefix}(\d+)$", os.path.basename(p))
        if m:
            seq_nums.append(int(m.group(1)))
    next_seq = max(seq_nums, default=0) + 1

    exp_name = f"{prefix}{next_seq:03d}"
    exp_dir = os.path.join(base, exp_name)
    frames_dir = os.path.join(exp_dir, "frames")
    os.makedirs(frames_dir)

    # update 'current' symlink
    link = os.path.join(base, "current")
    if os.path.islink(link):
        os.remove(link)
    os.symlink(exp_dir, link)

    print(exp_dir)


# ── save-frame ─────────────────────────────────────────────────────────────

def cmd_save_frame(args, config):
    exp_dir = _current_exp_dir(config)
    if not exp_dir:
        print("Error: no active experiment. Run 'init' first.", file=sys.stderr)
        sys.exit(1)

    frames_dir = os.path.join(exp_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    # determine sequence: count existing files for this round
    rnd = f"r{args.round:03d}"
    existing = glob.glob(os.path.join(frames_dir, f"{rnd}_*"))
    seq = len(existing) + 1

    label = args.label or "frame"
    ext = os.path.splitext(args.source)[1] or ".jpg"
    dest_name = f"{rnd}_{seq:03d}_{label}{ext}"
    dest = os.path.join(frames_dir, dest_name)

    shutil.copy2(args.source, dest)
    print(dest)


# ── hand-cache commands ───────────────────────────────────────────────────

def cmd_hand_load(args, config):
    cache_path = _hand_cache_path(config)
    cache = load_hand_cache(cache_path)
    print(json.dumps(cache, indent=2))


def cmd_hand_set(args, config):
    cache_path = _hand_cache_path(config)
    if not cache_path:
        print("Error: no active experiment. Run 'init' first.", file=sys.stderr)
        sys.exit(1)
    cache = load_hand_cache(cache_path)
    cache[args.position] = args.card
    save_hand_cache(cache_path, cache)
    print(json.dumps(cache, indent=2))


def cmd_hand_clear(args, config):
    cache_path = _hand_cache_path(config)
    if cache_path and os.path.exists(cache_path):
        os.remove(cache_path)


# ── main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Execution state & experiment manager")
    parser.add_argument(
        "--state-file", default=None,
        help="Override state file path (default: <current_exp>/state.json)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    sub.add_parser("init", help="Create new experiment directory")

    # load
    sub.add_parser("load", help="Print current state to stdout")

    # save
    p_save = sub.add_parser("save", help="Save execution state")
    p_save.add_argument("--phase", required=True,
                        choices=["recognizing", "deciding", "executing", "verifying"])
    p_save.add_argument("--round", type=int, default=0)
    p_save.add_argument("--action", default="{}", help="Current action JSON")
    p_save.add_argument("--commands", default="[]", help="Command sequence JSON array")
    p_save.add_argument("--completed", type=int, default=0)
    p_save.add_argument("--frame", default="", help="Path to last verified frame")

    # update
    p_update = sub.add_parser("update", help="Update fields in existing state")
    p_update.add_argument("--phase",
                          choices=["recognizing", "deciding", "executing", "verifying"])
    p_update.add_argument("--completed", type=int)
    p_update.add_argument("--frame", help="Path to last verified frame")

    # clear
    sub.add_parser("clear", help="Remove state file (keep experiment dir)")

    # save-frame
    p_frame = sub.add_parser("save-frame", help="Copy a frame into experiment dir")
    p_frame.add_argument("source", help="Source image path")
    p_frame.add_argument("--round", type=int, default=0, help="Current round number")
    p_frame.add_argument("--label", default="frame",
                         help="Label for the frame (e.g. capture, stable, verified)")

    # hand-load
    sub.add_parser("hand-load", help="Print current hand cache")

    # hand-set
    p_hand_set = sub.add_parser("hand-set", help="Cache a viewed card")
    p_hand_set.add_argument("--position", required=True, choices=["left", "right"])
    p_hand_set.add_argument("--card", required=True, help="Card notation (e.g. 9h)")

    # hand-clear
    sub.add_parser("hand-clear", help="Clear hand cache (between hands)")

    args = parser.parse_args()
    config = _load_config()

    if args.command == "init":
        cmd_init(args, config)
        return

    if args.command == "save-frame":
        cmd_save_frame(args, config)
        return

    if args.command == "hand-load":
        cmd_hand_load(args, config)
        return

    if args.command == "hand-set":
        cmd_hand_set(args, config)
        return

    if args.command == "hand-clear":
        cmd_hand_clear(args, config)
        return

    # resolve state path
    state_path = args.state_file or _default_state_path(config)

    if args.command == "load":
        state = load_state(state_path)
        if state is None:
            print("{}")
            sys.exit(1)
        print(json.dumps(state, indent=2))

    elif args.command == "save":
        if not state_path:
            print("Error: no active experiment. Run 'init' first.", file=sys.stderr)
            sys.exit(1)
        state = {
            "phase": args.phase,
            "round": args.round,
            "current_action": json.loads(args.action),
            "command_sequence": json.loads(args.commands),
            "commands_completed": args.completed,
            "last_verified_frame": args.frame,
        }
        save_state(state_path, state)

    elif args.command == "update":
        state = load_state(state_path)
        if state is None:
            print("Error: no existing state to update", file=sys.stderr)
            sys.exit(1)
        if args.phase is not None:
            state["phase"] = args.phase
        if args.completed is not None:
            state["commands_completed"] = args.completed
        if args.frame is not None:
            state["last_verified_frame"] = args.frame
        save_state(state_path, state)

    elif args.command == "clear":
        clear_state(state_path)


if __name__ == "__main__":
    main()
