#!/usr/bin/env python3
"""Shared DexHoldem V2 runtime helpers."""

import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


STAGES = ("idle", "atom_idle", "acting", "to_recover", "down", "show_hand", "win", "lose")
STAGE_SET = set(STAGES)
STATE_DIR_RE = re.compile(r"^s(\d+)$")
DEFAULT_LOOP_SAFETY = {
    "max_consecutive_waits": 20,
    "max_total_waits": 200,
    "max_step_retries": 2,
    "max_total_recoveries": 8,
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_config(path="config.yaml", *, missing_ok=True):
    if not path:
        return {}
    path = Path(path)
    if not path.exists():
        if missing_ok:
            return {}
        raise FileNotFoundError(f"config file not found: {path}")
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to read config.yaml; run preflight/uv sync first") from exc
    with path.open("r") as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"config file must contain a YAML mapping: {path}")
    return data


def loop_safety_limits(config):
    raw = (config.get("loop_safety", {}) or {}) if isinstance(config, dict) else {}
    limits = {}
    for key, default in DEFAULT_LOOP_SAFETY.items():
        value = raw.get(key, default)
        if isinstance(value, bool):
            raise ValueError(f"loop_safety.{key} must be an integer")
        value = int(value)
        if value < 0:
            raise ValueError(f"loop_safety.{key} must be non-negative")
        limits[key] = value
    return limits


def atomic_write_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as f:
        tmp = Path(f.name)
        try:
            f.write(content)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
    try:
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def atomic_write_json(path, data):
    atomic_write_text(path, json.dumps(data, indent=2) + "\n")


def atomic_copy(source, dest):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=dest.parent, prefix=f".{dest.name}.", suffix=".tmp", delete=False) as f:
        tmp = Path(f.name)
    try:
        shutil.copy2(source, tmp)
        os.replace(tmp, dest)
    finally:
        if tmp.exists():
            tmp.unlink()


def atomic_image_write(path, writer):
    """Write an image through writer(tmp_path), then atomically publish it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix or ".img"
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", suffix=suffix, delete=False) as f:
        tmp = Path(f.name)
    try:
        if not writer(str(tmp)):
            raise RuntimeError(f"failed to write image to {path}")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def read_json_file(path, *, default=None, missing_ok=False):
    path = Path(path)
    if not path.exists():
        if missing_ok:
            return default
        raise FileNotFoundError(f"JSON file not found: {path}")
    try:
        with path.open("r") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc


def extract_json_objects(markdown):
    objects = []
    for raw in re.findall(r"```json\s*(.*?)```", markdown, flags=re.S | re.I):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            objects.append(value)
    if objects:
        return objects

    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", markdown):
        try:
            value, _ = decoder.raw_decode(markdown[match.start() :])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            objects.append(value)
    return objects


def extract_json_object(markdown, predicate=None):
    for obj in extract_json_objects(markdown):
        if predicate is None or predicate(obj):
            return obj
    return None


def read_markdown_json(path, predicate=None):
    path = Path(path)
    if not path.exists():
        return None
    return extract_json_object(path.read_text(), predicate=predicate)


def state_index(path_or_name):
    name = Path(path_or_name).name
    match = STATE_DIR_RE.match(name)
    if not match:
        return None
    return int(match.group(1))


def sorted_state_dirs(exp_dir):
    states = []
    for path in Path(exp_dir).iterdir():
        if not path.is_dir():
            continue
        index = state_index(path.name)
        if index is not None:
            states.append((index, path))
    return [path for _, path in sorted(states, key=lambda item: item[0])]


def current_state_name(exp_dir):
    exp_dir = Path(exp_dir)
    link = exp_dir / "s_current"
    if link.exists():
        name = link.resolve().name
        if state_index(name) is None:
            raise RuntimeError(f"s_current points to a non-state directory: {name}")
        return name
    states = sorted_state_dirs(exp_dir)
    if not states:
        raise RuntimeError("no state folders found")
    return states[-1].name


def next_state_name(exp_dir):
    states = sorted_state_dirs(exp_dir)
    next_index = (state_index(states[-1].name) + 1) if states else 0
    return f"s{next_index}"


def sequence_steps(sequence_or_steps):
    if isinstance(sequence_or_steps, dict):
        return sequence_or_steps.get("steps", []) or []
    return sequence_or_steps or []


def first_pending_step(sequence_or_steps):
    for step in sequence_steps(sequence_or_steps):
        if step.get("status") != "completed":
            return step.get("name")
    return None


def step_status(sequence_or_steps, step_name):
    for step in sequence_steps(sequence_or_steps):
        if step.get("name") == step_name:
            return step.get("status", "pending")
    return None


def view_slot_from_intent(intent):
    if intent in ("view_left_hole_card", "show_left_hole_card"):
        return "left"
    if intent in ("view_right_hole_card", "show_right_hole_card"):
        return "right"
    return None


def cached_command_for_step(sequence, step_name):
    if not step_name:
        raise RuntimeError("current step is not set")
    for step in sequence_steps(sequence):
        if step.get("name") == step_name and step.get("last_command"):
            return step.get("command_index"), step["last_command"], step.get("last_prefix")

    plan = sequence.get("plan") or {}
    commands = plan.get("commands") or []
    command_steps = plan.get("command_steps") or []
    for index, name in enumerate(command_steps):
        if name == step_name:
            if index >= len(commands):
                raise RuntimeError(f"cached command step has no command: {step_name}")
            prefix = plan.get("prefix") if index == 0 else None
            return index, commands[index], prefix
    raise RuntimeError(f"current step is not a cached robot command step: {step_name}")


def has_cached_command_step(sequence, step_name):
    try:
        cached_command_for_step(sequence, step_name)
    except RuntimeError:
        return False
    return True
