#!/usr/bin/env python3
"""DexHoldem V2 experiment/state-folder manager."""

import argparse
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


STAGES = {"idle", "atom_idle", "acting", "to_recover", "down", "show_hand", "win", "lose"}
CHIP_TEMPLATE = {"5": 0, "10": 0, "50": 0, "100": 0}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path, default):
    path = Path(path)
    if not path.exists():
        return default
    with path.open("r") as f:
        return json.load(f)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{int(time.time() * 1000000)}.tmp")
    with tmp.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def replace_symlink(link, target):
    link = Path(link)
    if link.is_symlink() or link.exists():
        if link.is_dir() and not link.is_symlink():
            raise RuntimeError(f"{link} exists and is not a symlink")
        link.unlink()
    link.symlink_to(target)


def default_hole_cache():
    return {
        "schema_version": 1,
        "left": {"card": None, "status": "unknown", "source_state": None, "confidence": 0.0},
        "right": {"card": None, "status": "unknown", "source_state": None, "confidence": 0.0},
        "blinds": {
            "dealer": None,
            "small_blind": None,
            "big_blind": None,
            "source_state": None,
            "status": "unknown",
        },
    }


def default_action_sequence():
    return {
        "schema_version": 1,
        "sequence_id": None,
        "loop_stage": "idle",
        "intent": None,
        "action": None,
        "plan": None,
        "steps": [],
        "current_step": None,
        "retry_count": 0,
        "last_error": None,
        "human_required": False,
        "updated_at": utc_now(),
    }


def load_config(path):
    if not path or not Path(path).exists():
        return {}
    try:
        import yaml
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {}


def resolve_exp_dir(args):
    if getattr(args, "exp_dir", None):
        return Path(args.exp_dir).resolve()
    cwd = Path.cwd()
    if (cwd / "s_current").exists() or (cwd / "hole_card_cache.json").exists():
        return cwd.resolve()
    link = cwd / "experiments" / "current"
    if link.exists():
        return link.resolve()
    raise RuntimeError("could not resolve experiment dir; run from an experiment root or pass --exp-dir")


def current_state_name(exp_dir):
    link = exp_dir / "s_current"
    if link.exists():
        return link.resolve().name
    states = sorted([p.name for p in exp_dir.glob("s[0-9]*") if p.is_dir()], key=lambda x: int(x[1:]))
    if not states:
        raise RuntimeError("no state folders found")
    return states[-1]


def current_state_dir(exp_dir):
    return exp_dir / current_state_name(exp_dir)


def state_dir(exp_dir, name=None):
    if name:
        return exp_dir / name
    return current_state_dir(exp_dir)


def extract_json_block(markdown):
    blocks = re.findall(r"```json\s*(.*?)```", markdown, flags=re.S)
    for block in blocks:
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue
    match = re.search(r"(\{.*\})", markdown, flags=re.S)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


def read_markdown_json(path):
    path = Path(path)
    if not path.exists():
        return None
    return extract_json_block(path.read_text())


def sorted_state_dirs(exp_dir):
    return sorted(
        [p for p in Path(exp_dir).glob("s[0-9]*") if p.is_dir()],
        key=lambda p: int(p.name[1:]),
    )


def latest_state_with(exp_dir, filename):
    found = [p for p in sorted_state_dirs(exp_dir) if (p / filename).exists()]
    return found[-1] if found else None


def load_hole_cache(exp_dir):
    cache = read_json(exp_dir / "hole_card_cache.json", default_hole_cache())
    default = default_hole_cache()
    for key, value in default.items():
        cache.setdefault(key, value)
    return cache


def save_hole_cache(exp_dir, cache):
    write_json(exp_dir / "hole_card_cache.json", cache)


def load_sequence(exp_dir):
    seq = read_json(exp_dir / "action_sequence.json", default_action_sequence())
    seq.setdefault("loop_stage", "idle")
    seq.setdefault("plan", None)
    seq.setdefault("steps", [])
    seq.setdefault("human_required", False)
    return seq


def save_sequence(exp_dir, seq):
    seq["updated_at"] = utc_now()
    write_json(exp_dir / "action_sequence.json", seq)


def cmd_init_experiment(args):
    config = load_config(args.config)
    base = Path(args.base_dir or (config.get("experiments", {}) or {}).get("base_dir", "./experiments"))
    if not base.is_absolute():
        base = Path.cwd() / base
    base.mkdir(parents=True, exist_ok=True)

    exp_name = args.exp_name or datetime.now().strftime("exp%Y%m%d_%H%M%S")
    exp_dir = base / exp_name
    exp_dir.mkdir(parents=True, exist_ok=True)
    (exp_dir / "s0").mkdir(exist_ok=True)
    replace_symlink(exp_dir / "s_current", "s0")
    replace_symlink(base / "current", exp_dir)

    save_hole_cache(exp_dir, default_hole_cache())
    save_sequence(exp_dir, default_action_sequence())
    print(json.dumps({"status": "ok", "exp_dir": str(exp_dir), "current_state": "s0"}, indent=2))


def cmd_current(args):
    exp_dir = resolve_exp_dir(args)
    name = current_state_name(exp_dir)
    print(json.dumps({"exp_dir": str(exp_dir), "state": name, "state_dir": str(exp_dir / name)}, indent=2))


def copy_or_read_source(source):
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text()


def cmd_save_capture(args):
    exp_dir = resolve_exp_dir(args)
    sdir = state_dir(exp_dir, args.state)
    sdir.mkdir(parents=True, exist_ok=True)
    dest = sdir / "00_capture.jpg"
    shutil.copy2(args.source, dest)
    print(json.dumps({"status": "ok", "path": str(dest)}, indent=2))


def cmd_save_markdown(args, filename):
    exp_dir = resolve_exp_dir(args)
    sdir = state_dir(exp_dir, args.state)
    sdir.mkdir(parents=True, exist_ok=True)
    content = copy_or_read_source(args.source)
    dest = sdir / filename
    dest.write_text(content)
    print(json.dumps({"status": "ok", "path": str(dest)}, indent=2))


def cmd_begin_next(args):
    exp_dir = resolve_exp_dir(args)
    after = args.after or current_state_name(exp_dir)
    after_dir = exp_dir / after
    if not (after_dir / "02_action.md").exists() and not args.allow_missing_action:
        raise RuntimeError(f"{after}/02_action.md does not exist; refusing to create next state")

    states = [int(p.name[1:]) for p in exp_dir.glob("s[0-9]*") if p.is_dir()]
    next_name = f"s{max(states, default=-1) + 1}"
    (exp_dir / next_name).mkdir()
    replace_symlink(exp_dir / "s_current", next_name)
    print(json.dumps({"status": "ok", "state": next_name, "state_dir": str(exp_dir / next_name)}, indent=2))


def parse_steps(args):
    if args.steps_json:
        raw = json.loads(args.steps_json)
        return normalize_steps(raw)
    if args.steps:
        return normalize_steps([x.strip() for x in args.steps.split(",") if x.strip()])
    return []


def normalize_steps(raw):
    steps = []
    for item in raw or []:
        if isinstance(item, dict):
            name = item.get("name")
            if not name:
                raise RuntimeError("sequence step is missing name")
            step = dict(item)
            step.setdefault("status", "pending")
        else:
            step = {"name": str(item), "status": "pending"}
        steps.append(step)
    return steps


def first_pending_step(steps):
    for step in steps:
        if step.get("status") != "completed":
            return step.get("name")
    return None


def cmd_start_action(args):
    exp_dir = resolve_exp_dir(args)
    if args.sequence_json:
        seq = json.loads(args.sequence_json)
        if not isinstance(seq, dict):
            raise RuntimeError("--sequence-json must decode to an object")
        if args.intent:
            seq["intent"] = args.intent
        if args.action_json:
            seq["action"] = json.loads(args.action_json)
        if args.steps or args.steps_json:
            seq["steps"] = parse_steps(args)
        seq.setdefault("schema_version", 1)
        if args.sequence_id:
            seq["sequence_id"] = args.sequence_id
        if not seq.get("sequence_id"):
            seq["sequence_id"] = f"seq_{int(time.time())}"
        seq.setdefault("loop_stage", "acting")
        if seq["loop_stage"] not in STAGES:
            raise RuntimeError(f"invalid loop stage: {seq['loop_stage']}")
        if not seq.get("intent"):
            raise RuntimeError("sequence is missing intent")
        seq.setdefault("action", None)
        seq.setdefault("plan", None)
        seq["steps"] = normalize_steps(seq.get("steps", []))
        seq["current_step"] = seq.get("current_step") or first_pending_step(seq["steps"])
        seq.setdefault("retry_count", 0)
        seq.setdefault("last_error", None)
        seq.setdefault("human_required", False)
    else:
        if not args.intent:
            raise RuntimeError("--intent is required unless --sequence-json is provided")
        action = json.loads(args.action_json) if args.action_json else None
        steps = parse_steps(args)
        seq = {
            "schema_version": 1,
            "sequence_id": args.sequence_id or f"seq_{int(time.time())}",
            "loop_stage": "acting",
            "intent": args.intent,
            "action": action,
            "plan": None,
            "steps": steps,
            "current_step": first_pending_step(steps),
            "retry_count": 0,
            "last_error": None,
            "human_required": False,
            "updated_at": utc_now(),
        }
    save_sequence(exp_dir, seq)
    print(json.dumps(seq, indent=2))


def cmd_complete_step(args):
    exp_dir = resolve_exp_dir(args)
    seq = load_sequence(exp_dir)
    found = False
    for idx, step in enumerate(seq.get("steps", [])):
        if step.get("name") == args.step:
            step["status"] = "completed"
            step["completed_at"] = utc_now()
            found = True
            pending = [s for s in seq["steps"][idx + 1:] if s.get("status") != "completed"]
            seq["current_step"] = pending[0]["name"] if pending else None
            break
    if not found:
        raise RuntimeError(f"step not found: {args.step}")
    save_sequence(exp_dir, seq)
    print(json.dumps(seq, indent=2))


def cmd_set_loop_stage(args):
    if args.stage not in STAGES:
        raise RuntimeError(f"invalid loop stage: {args.stage}")
    exp_dir = resolve_exp_dir(args)
    seq = load_sequence(exp_dir)
    seq["loop_stage"] = args.stage
    save_sequence(exp_dir, seq)
    print(json.dumps(seq, indent=2))


def cmd_complete_action(args):
    exp_dir = resolve_exp_dir(args)
    seq = load_sequence(exp_dir)
    for step in seq.get("steps", []):
        if step.get("status") == "pending":
            step["status"] = "completed"
            step["completed_at"] = utc_now()
    seq["current_step"] = None
    seq["loop_stage"] = args.loop_stage
    seq["last_error"] = None
    seq["human_required"] = False
    save_sequence(exp_dir, seq)
    print(json.dumps(seq, indent=2))


def cmd_fail(args):
    exp_dir = resolve_exp_dir(args)
    seq = load_sequence(exp_dir)
    seq["loop_stage"] = "down"
    seq["last_error"] = {
        "code": args.code,
        "message": args.message,
        "retryable": args.retryable == "true",
        "at": utc_now(),
    }
    seq["human_required"] = args.human_required
    if args.human_required:
        seq["resume_options"] = args.resume_options.split(",") if args.resume_options else []
    save_sequence(exp_dir, seq)
    print(json.dumps(seq, indent=2))


def cmd_require_human(args):
    exp_dir = resolve_exp_dir(args)
    seq = load_sequence(exp_dir)
    seq["loop_stage"] = "down"
    seq["human_required"] = True
    seq["last_error"] = {
        "code": "human_required",
        "message": args.reason,
        "retryable": False,
        "at": utc_now(),
    }
    seq["resume_options"] = args.resume_options.split(",") if args.resume_options else []
    save_sequence(exp_dir, seq)
    print(json.dumps(seq, indent=2))


def cmd_cache_card(args):
    exp_dir = resolve_exp_dir(args)
    cache = load_hole_cache(exp_dir)
    cache[args.slot] = {
        "card": args.card,
        "status": args.status,
        "source_state": args.source_state or current_state_name(exp_dir),
        "confidence": args.confidence,
    }
    save_hole_cache(exp_dir, cache)
    print(json.dumps(cache, indent=2))


def cmd_set_blinds(args):
    exp_dir = resolve_exp_dir(args)
    cache = load_hole_cache(exp_dir)
    cache["blinds"] = {
        "dealer": args.dealer,
        "small_blind": args.small_blind,
        "big_blind": args.big_blind,
        "source_state": args.source_state or current_state_name(exp_dir),
        "status": args.status,
    }
    if args.note:
        cache["blinds"]["note"] = args.note
    save_hole_cache(exp_dir, cache)
    print(json.dumps(cache, indent=2))


def cmd_clear_hand(args):
    exp_dir = resolve_exp_dir(args)
    existing = load_hole_cache(exp_dir)
    cache = default_hole_cache()
    cache["blinds"] = existing.get("blinds", cache["blinds"])
    save_hole_cache(exp_dir, cache)
    print(json.dumps(cache, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(description="DexHoldem V2 state manager")
    parser.add_argument("--exp-dir", help="Experiment root; defaults to cwd or experiments/current")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init-experiment")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--base-dir")
    p.add_argument("--exp-name")

    sub.add_parser("current")

    p = sub.add_parser("save-capture")
    p.add_argument("--source", required=True)
    p.add_argument("--state")

    p = sub.add_parser("save-parsed")
    p.add_argument("--source", required=True)
    p.add_argument("--state")

    p = sub.add_parser("save-action")
    p.add_argument("--source", required=True)
    p.add_argument("--state")

    p = sub.add_parser("begin-next")
    p.add_argument("--after")
    p.add_argument("--allow-missing-action", action="store_true")

    p = sub.add_parser("start-action")
    p.add_argument("--intent")
    p.add_argument("--action-json")
    p.add_argument("--steps")
    p.add_argument("--steps-json")
    p.add_argument("--sequence-json")
    p.add_argument("--sequence-id")

    p = sub.add_parser("complete-step")
    p.add_argument("--step", required=True)

    p = sub.add_parser("complete-action")
    p.add_argument("--loop-stage", default="idle", choices=sorted(STAGES))

    p = sub.add_parser("set-loop-stage")
    p.add_argument("--stage", required=True, choices=sorted(STAGES))

    p = sub.add_parser("fail")
    p.add_argument("--code", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--retryable", required=True, choices=["true", "false"])
    p.add_argument("--human-required", action="store_true")
    p.add_argument("--resume-options", default="")

    p = sub.add_parser("require-human")
    p.add_argument("--reason", required=True)
    p.add_argument("--resume-options", default="")

    p = sub.add_parser("cache-card")
    p.add_argument("--slot", required=True, choices=["left", "right"])
    p.add_argument("--card", required=True)
    p.add_argument("--confidence", type=float, default=1.0)
    p.add_argument("--source-state")
    p.add_argument("--status", default="cached", choices=["unknown", "viewing", "cached", "put_down", "invalid"])

    p = sub.add_parser("set-blinds")
    p.add_argument("--dealer", required=True, choices=["robot", "opponent", "unclear"])
    p.add_argument("--small-blind", required=True, choices=["robot", "opponent", "unclear"])
    p.add_argument("--big-blind", required=True, choices=["robot", "opponent", "unclear"])
    p.add_argument("--source-state")
    p.add_argument("--status", default="recognized", choices=["recognized", "unclear", "conflict"])
    p.add_argument("--note")

    sub.add_parser("clear-hand")

    return parser


def main():
    args = build_parser().parse_args()
    try:
        if args.command == "init-experiment":
            cmd_init_experiment(args)
        elif args.command == "current":
            cmd_current(args)
        elif args.command == "save-capture":
            cmd_save_capture(args)
        elif args.command == "save-parsed":
            cmd_save_markdown(args, "01_parsed_state.md")
        elif args.command == "save-action":
            cmd_save_markdown(args, "02_action.md")
        elif args.command == "begin-next":
            cmd_begin_next(args)
        elif args.command == "start-action":
            cmd_start_action(args)
        elif args.command == "complete-step":
            cmd_complete_step(args)
        elif args.command == "set-loop-stage":
            cmd_set_loop_stage(args)
        elif args.command == "complete-action":
            cmd_complete_action(args)
        elif args.command == "fail":
            cmd_fail(args)
        elif args.command == "require-human":
            cmd_require_human(args)
        elif args.command == "cache-card":
            cmd_cache_card(args)
        elif args.command == "set-blinds":
            cmd_set_blinds(args)
        elif args.command == "clear-hand":
            cmd_clear_hand(args)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
