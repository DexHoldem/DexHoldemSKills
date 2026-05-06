#!/usr/bin/env python3
"""DexHoldem V2 experiment/state-folder manager."""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from utils import (
    STAGE_SET,
    STAGES,
    atomic_copy,
    atomic_write_json,
    atomic_write_text,
    current_state_name as util_current_state_name,
    first_pending_step,
    load_config,
    next_state_name,
    read_json_file,
    utc_now,
)

def read_json(path, default):
    return read_json_file(path, default=default, missing_ok=True)


def write_json(path, data):
    atomic_write_json(path, data)


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
        "safety_counters": default_safety_counters(),
        "updated_at": utc_now(),
    }


def default_safety_counters():
    return {
        "consecutive_waits": 0,
        "total_waits": 0,
        "consecutive_recoveries": 0,
        "total_recoveries": 0,
        "executor_failures": 0,
        "action_sequences_started": 0,
        "human_help_requests": 0,
    }


def normalize_safety_counters(seq):
    counters = seq.setdefault("safety_counters", {})
    for key, value in default_safety_counters().items():
        counters.setdefault(key, value)
    return counters


def reset_consecutive_waits(seq):
    normalize_safety_counters(seq)["consecutive_waits"] = 0


def reset_consecutive_recoveries(seq):
    normalize_safety_counters(seq)["consecutive_recoveries"] = 0


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
    return util_current_state_name(exp_dir)


def current_state_dir(exp_dir):
    return exp_dir / current_state_name(exp_dir)


def state_dir(exp_dir, name=None):
    if name:
        return exp_dir / name
    return current_state_dir(exp_dir)


def load_hole_cache(exp_dir):
    cache = read_json(exp_dir / "hole_card_cache.json", default_hole_cache())
    default = default_hole_cache()
    for key, value in default.items():
        cache.setdefault(key, value)
    return cache


def save_hole_cache(exp_dir, cache):
    write_json(exp_dir / "hole_card_cache.json", cache)


HUMAN_HELP_CACHE_FILE = "human_help_request.json"


def create_human_help_cache(exp_dir, reason, resume_options=None, context=None):
    """Create a cache file indicating human help is requested."""
    cache = {
        "schema_version": 1,
        "requested_at": utc_now(),
        "reason": reason,
        "resume_options": resume_options or [],
        "context": context or {},
        "state_name": current_state_name(exp_dir),
    }
    write_json(exp_dir / HUMAN_HELP_CACHE_FILE, cache)
    return cache


def load_human_help_cache(exp_dir):
    """Load the human help request cache if it exists."""
    return read_json(exp_dir / HUMAN_HELP_CACHE_FILE, None)


def remove_human_help_cache(exp_dir):
    """Remove the human help cache after human has helped."""
    cache_path = Path(exp_dir) / HUMAN_HELP_CACHE_FILE
    if cache_path.exists():
        cache_path.unlink()
        return True
    return False


def human_help_requested(exp_dir):
    """Check if human help is currently requested."""
    return (Path(exp_dir) / HUMAN_HELP_CACHE_FILE).exists()


def load_sequence(exp_dir):
    seq = read_json(exp_dir / "action_sequence.json", default_action_sequence())
    seq.setdefault("loop_stage", "idle")
    seq.setdefault("plan", None)
    seq.setdefault("steps", [])
    seq.setdefault("human_required", False)
    normalize_safety_counters(seq)
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
    atomic_copy(args.source, dest)
    print(json.dumps({"status": "ok", "path": str(dest)}, indent=2))


def cmd_save_markdown(args, filename):
    exp_dir = resolve_exp_dir(args)
    sdir = state_dir(exp_dir, args.state)
    sdir.mkdir(parents=True, exist_ok=True)
    content = copy_or_read_source(args.source)
    dest = sdir / filename
    atomic_write_text(dest, content)
    print(json.dumps({"status": "ok", "path": str(dest)}, indent=2))


def cmd_begin_next(args):
    exp_dir = resolve_exp_dir(args)
    after = args.after or current_state_name(exp_dir)
    after_dir = exp_dir / after
    if not (after_dir / "02_action.md").exists() and not args.allow_missing_action:
        raise RuntimeError(f"{after}/02_action.md does not exist; refusing to create next state")

    next_name = next_state_name(exp_dir)
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


def cmd_start_action(args):
    exp_dir = resolve_exp_dir(args)
    previous_seq = load_sequence(exp_dir)
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
        if seq["loop_stage"] not in STAGE_SET:
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
            "safety_counters": default_safety_counters(),
            "updated_at": utc_now(),
        }
    seq["safety_counters"] = normalize_safety_counters(previous_seq).copy()
    counters = normalize_safety_counters(seq)
    counters["consecutive_waits"] = 0
    counters["consecutive_recoveries"] = 0
    counters["action_sequences_started"] = int(counters.get("action_sequences_started", 0)) + 1
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


def cmd_dispatch_step(args):
    exp_dir = resolve_exp_dir(args)
    seq = load_sequence(exp_dir)
    found = False
    for step in seq.get("steps", []):
        if step.get("name") == args.step:
            if step.get("status") == "completed":
                raise RuntimeError(f"step is already completed: {args.step}")
            if step.get("status") == "dispatched":
                raise RuntimeError(f"step is already dispatched: {args.step}")
            step["status"] = "dispatched"
            step["dispatched_at"] = utc_now()
            if args.robot_command:
                step["last_command"] = args.robot_command
            if args.prefix is not None:
                step["last_prefix"] = args.prefix or None
            if args.command_index is not None:
                step["command_index"] = args.command_index
            found = True
            break
    if not found:
        raise RuntimeError(f"step not found: {args.step}")
    seq["current_step"] = args.step
    seq["loop_stage"] = "acting"
    reset_consecutive_waits(seq)
    save_sequence(exp_dir, seq)
    print(json.dumps(seq, indent=2))


def cmd_prepare_retry(args):
    exp_dir = resolve_exp_dir(args)
    seq = load_sequence(exp_dir)
    step_name = args.step or seq.get("current_step") or first_pending_step(seq.get("steps", []))
    if not step_name:
        raise RuntimeError("no current step to retry")
    retry_count = int(seq.get("retry_count", 0))
    if args.max_retries is not None and retry_count >= args.max_retries:
        raise RuntimeError(f"retry limit reached: {retry_count}/{args.max_retries}")
    counters = normalize_safety_counters(seq)
    total_recoveries = int(counters.get("total_recoveries", 0))
    if args.max_total_recoveries is not None and total_recoveries >= args.max_total_recoveries:
        seq["loop_stage"] = "down"
        seq["human_required"] = True
        seq["last_error"] = {
            "code": "total_recovery_limit_reached",
            "message": f"total recovery limit reached: {total_recoveries}/{args.max_total_recoveries}",
            "retryable": False,
            "at": utc_now(),
        }
        save_sequence(exp_dir, seq)
        raise RuntimeError(seq["last_error"]["message"])

    found = False
    for step in seq.get("steps", []):
        if step.get("name") == step_name:
            if step.get("status") == "completed":
                raise RuntimeError(f"cannot retry completed step: {step_name}")
            step["status"] = "pending"
            step["retry_prepared_at"] = utc_now()
            found = True
            break
    if not found:
        raise RuntimeError(f"step not found: {step_name}")

    seq["retry_count"] = retry_count + 1
    seq["current_step"] = step_name
    seq["loop_stage"] = "atom_idle"
    counters["consecutive_waits"] = 0
    counters["consecutive_recoveries"] = int(counters.get("consecutive_recoveries", 0)) + 1
    counters["total_recoveries"] = total_recoveries + 1
    history = seq.setdefault("retry_history", [])
    history.append(
        {
            "step": step_name,
            "reason": args.reason,
            "retry_number": seq["retry_count"],
            "at": utc_now(),
        }
    )
    save_sequence(exp_dir, seq)
    print(json.dumps(seq, indent=2))


def cmd_set_loop_stage(args):
    if args.stage not in STAGE_SET:
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
        if step.get("status") != "completed":
            step["status"] = "completed"
            step["completed_at"] = utc_now()
    seq["current_step"] = None
    seq["loop_stage"] = args.loop_stage
    seq["last_error"] = None
    seq["human_required"] = False
    reset_consecutive_waits(seq)
    reset_consecutive_recoveries(seq)
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
    counters = normalize_safety_counters(seq)
    if args.code == "executor_failed":
        counters["executor_failures"] = int(counters.get("executor_failures", 0)) + 1
    save_sequence(exp_dir, seq)
    print(json.dumps(seq, indent=2))


def cmd_record_wait(args):
    exp_dir = resolve_exp_dir(args)
    seq = load_sequence(exp_dir)
    counters = normalize_safety_counters(seq)
    counters["consecutive_waits"] = int(counters.get("consecutive_waits", 0)) + 1
    counters["total_waits"] = int(counters.get("total_waits", 0)) + 1
    counters["last_wait_reason"] = args.reason
    counters["last_wait_at"] = utc_now()

    limit_reached = False
    limit_reason = None
    if args.max_consecutive_waits is not None and counters["consecutive_waits"] > args.max_consecutive_waits:
        limit_reached = True
        limit_reason = (
            f"consecutive wait limit reached: "
            f"{counters['consecutive_waits']}/{args.max_consecutive_waits}"
        )
    if args.max_total_waits is not None and counters["total_waits"] > args.max_total_waits:
        limit_reached = True
        limit_reason = f"total wait limit reached: {counters['total_waits']}/{args.max_total_waits}"

    if limit_reached:
        seq["loop_stage"] = "down"
        seq["human_required"] = True
        seq["last_error"] = {
            "code": "wait_limit_reached",
            "message": limit_reason,
            "retryable": False,
            "at": utc_now(),
        }

    save_sequence(exp_dir, seq)
    print(json.dumps({"sequence": seq, "limit_reached": limit_reached, "limit_reason": limit_reason}, indent=2))


def cmd_reset_safety(args):
    exp_dir = resolve_exp_dir(args)
    seq = load_sequence(exp_dir)
    counters = normalize_safety_counters(seq)
    if args.scope == "all":
        seq["safety_counters"] = default_safety_counters()
    else:
        counters["consecutive_waits"] = 0
        counters["consecutive_recoveries"] = 0
    seq["last_error"] = None
    seq["human_required"] = False
    seq.setdefault("safety_resets", []).append(
        {
            "scope": args.scope,
            "reason": args.reason,
            "at": utc_now(),
        }
    )
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
    resume_options = args.resume_options.split(",") if args.resume_options else []
    seq["resume_options"] = resume_options
    counters = normalize_safety_counters(seq)
    counters["human_help_requests"] = int(counters.get("human_help_requests", 0)) + 1
    save_sequence(exp_dir, seq)
    create_human_help_cache(exp_dir, args.reason, resume_options)
    print(json.dumps(seq, indent=2))


def cmd_ack_human_help(args):
    """Acknowledge human help - removes the cache and optionally resets safety."""
    exp_dir = resolve_exp_dir(args)
    cache = load_human_help_cache(exp_dir)
    removed = remove_human_help_cache(exp_dir)
    seq = load_sequence(exp_dir)
    seq["human_required"] = False
    if args.reset_safety:
        reset_consecutive_waits(seq)
        reset_consecutive_recoveries(seq)
    if args.set_stage:
        if args.set_stage not in STAGE_SET:
            raise ValueError(f"invalid stage: {args.set_stage}, must be one of {STAGES}")
        seq["loop_stage"] = args.set_stage
    save_sequence(exp_dir, seq)
    print(json.dumps({
        "status": "ok",
        "cache_removed": removed,
        "previous_request": cache,
        "sequence": seq,
    }, indent=2))


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


def cmd_next_hand(args):
    exp_dir = resolve_exp_dir(args)
    existing = load_hole_cache(exp_dir)
    previous_seq = load_sequence(exp_dir)
    cache = default_hole_cache()
    if not args.refresh_blinds:
        cache["blinds"] = existing.get("blinds", cache["blinds"])
    seq = default_action_sequence()
    seq["safety_counters"] = normalize_safety_counters(previous_seq).copy()
    seq["safety_counters"]["consecutive_waits"] = 0
    seq["safety_counters"]["consecutive_recoveries"] = 0
    seq["post_hand_reset"] = {
        "at": utc_now(),
        "refresh_blinds": bool(args.refresh_blinds),
        "note": args.note,
    }
    save_hole_cache(exp_dir, cache)
    save_sequence(exp_dir, seq)
    print(json.dumps({"hole_card_cache": cache, "action_sequence": seq}, indent=2))


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

    p = sub.add_parser("dispatch-step")
    p.add_argument("--step", required=True)
    p.add_argument("--robot-command")
    p.add_argument("--prefix")
    p.add_argument("--command-index", type=int)

    p = sub.add_parser("prepare-retry")
    p.add_argument("--step")
    p.add_argument("--reason", default="retryable_recovery")
    p.add_argument("--max-retries", type=int, default=2)
    p.add_argument("--max-total-recoveries", type=int, default=8)

    p = sub.add_parser("record-wait")
    p.add_argument("--reason", default="wait")
    p.add_argument("--max-consecutive-waits", type=int, default=20)
    p.add_argument("--max-total-waits", type=int, default=200)

    p = sub.add_parser("reset-safety")
    p.add_argument("--scope", choices=["consecutive", "all"], default="consecutive")
    p.add_argument("--reason", default="human_confirmed_resume")

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

    p = sub.add_parser("ack-human-help")
    p.add_argument("--reset-safety", action="store_true", help="Reset consecutive waits and recoveries")
    p.add_argument("--set-stage", choices=STAGES, help="Set loop stage after acknowledgment")

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

    p = sub.add_parser("next-hand")
    p.add_argument("--refresh-blinds", action="store_true")
    p.add_argument("--note", default="post_hand_reset")

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
        elif args.command == "dispatch-step":
            cmd_dispatch_step(args)
        elif args.command == "prepare-retry":
            cmd_prepare_retry(args)
        elif args.command == "record-wait":
            cmd_record_wait(args)
        elif args.command == "reset-safety":
            cmd_reset_safety(args)
        elif args.command == "set-loop-stage":
            cmd_set_loop_stage(args)
        elif args.command == "complete-action":
            cmd_complete_action(args)
        elif args.command == "fail":
            cmd_fail(args)
        elif args.command == "require-human":
            cmd_require_human(args)
        elif args.command == "ack-human-help":
            cmd_ack_human_help(args)
        elif args.command == "cache-card":
            cmd_cache_card(args)
        elif args.command == "set-blinds":
            cmd_set_blinds(args)
        elif args.command == "clear-hand":
            cmd_clear_hand(args)
        elif args.command == "next-hand":
            cmd_next_hand(args)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
