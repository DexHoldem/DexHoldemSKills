#!/usr/bin/env python3
"""DexHoldem V2 per-state router.

This script encodes the SKILL.md per-state if/else flow and returns a JSON
judgment. It does not parse images, choose poker strategy, or decide unsafe
physical recovery by itself.
"""

import argparse
import json
import shlex
from pathlib import Path

from utils import (
    STAGE_SET,
    current_state_name,
    extract_json_objects,
    first_pending_step,
    has_cached_command_step,
    load_config,
    loop_safety_limits,
    read_json_file,
    step_status,
    view_slot_from_intent,
)

WAIT_SECONDS = 3
ALWAYS_REQUIRED_TABLE_FIELDS = (
    "scene_stable",
    "is_my_turn",
)
IDLE_TABLE_FIELDS = (
    "scene_stable",
    "is_my_turn",
    "community_cards",
    "my_chips",
    "opponent_chips",
    "my_current_bet",
    "opponent_bet",
)
STAGE_REQUIRED_TABLE_FIELDS = {
    "idle": IDLE_TABLE_FIELDS,
    "show_hand": ("community_cards",),
    "win": ("my_current_bet", "opponent_bet"),
}


def read_json(path):
    path = Path(path)
    try:
        return read_json_file(path), None
    except (FileNotFoundError, ValueError) as exc:
        return None, str(exc)


def read_markdown_json(path, predicate=None):
    path = Path(path)
    if not path.exists():
        return None, f"{path.name} is missing"
    try:
        blocks = extract_json_objects(path.read_text())
    except OSError as exc:
        return None, f"could not read {path.name}: {exc}"
    for block in blocks:
        if predicate is None or predicate(block):
            return block, None
    return None, f"{path.name} has no matching JSON block"


def resolve_exp_dir(path=None):
    if path:
        return Path(path).resolve()
    cwd = Path.cwd()
    if (cwd / "s_current").exists() or (cwd / "hole_card_cache.json").exists():
        return cwd.resolve()
    current = cwd / "experiments" / "current"
    if current.exists():
        return current.resolve()
    raise RuntimeError("run from an experiment root or pass --exp-dir")


def command_for_action(action):
    encoded = json.dumps(action, separators=(",", ":"))
    return f"python3 executor.py --action {shlex.quote(encoded)}"


def command_for_begin_next(state_name):
    return [
        f"python3 state.py begin-next --after {state_name}",
        "python3 capture.py --output s_current/00_capture.jpg",
    ]


def route(exp_dir, state_name, state_dir, route_name, reason, judgments, **extra):
    data = {
        "status": "ok",
        "exp_dir": str(exp_dir),
        "state": state_name,
        "state_dir": str(state_dir),
        "route": route_name,
        "reason": reason,
        "judged_results": judgments,
    }
    data.update(extra)
    return data


def add(judgments, check, result, reason, **extra):
    item = {"check": check, "result": result, "reason": reason}
    if extra:
        item.update(extra)
    judgments.append(item)


def cached_card(cache, slot):
    item = cache.get(slot, {}) if isinstance(cache, dict) else {}
    return item.get("status") == "cached" and bool(item.get("card"))


def next_unknown_hole(cache):
    for slot in ("left", "right"):
        if not cached_card(cache, slot):
            return slot
    return None


def table_missing_fields(table, loop_stage):
    required = STAGE_REQUIRED_TABLE_FIELDS.get(loop_stage, ())
    missing = []
    for name in ALWAYS_REQUIRED_TABLE_FIELDS + tuple(required):
        if name not in table and name not in missing:
            missing.append(name)
    return missing


def uncertain_fields(table):
    value = table.get("uncertain_fields", [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return ["uncertain_fields"]


def collection_uncertain_fields(fields):
    relevant = []
    for field in fields:
        name = field.lower()
        if "bet" in name or "collection" in name or "winnings" in name or name in ("table", "my_current_bet", "opponent_bet"):
            relevant.append(field)
    return relevant


def wait_action(reason, wait_seconds):
    return {"action": "wait", "reason": reason, "sleep_seconds": wait_seconds}


def safety_counters(sequence):
    counters = sequence.get("safety_counters", {}) if isinstance(sequence, dict) else {}
    return counters if isinstance(counters, dict) else {}


def route_request_human(exp_dir, state_name, state_dir, judgments, reason_key, message, context=None):
    action = {
        "action": "request_human",
        "reason": message,
        "resume_options": ["inspect_scene", "reset_consecutive_safety", "reset_all_safety", "abort_hand"],
    }
    return route(
        exp_dir,
        state_name,
        state_dir,
        reason_key,
        message,
        judgments,
        agent_required=False,
        suggested_action=action,
        commands=[command_for_action(action)],
        context=context or {},
    )


def route_wait(exp_dir, state_name, state_dir, judgments, reason_key, message, wait_seconds, sequence=None, limits=None):
    counters = safety_counters(sequence)
    limits = limits or loop_safety_limits({})
    next_consecutive = int(counters.get("consecutive_waits", 0)) + 1
    next_total = int(counters.get("total_waits", 0)) + 1
    if limits["max_consecutive_waits"] is not None and next_consecutive > limits["max_consecutive_waits"]:
        add(
            judgments,
            "wait_limit",
            False,
            "next wait would exceed max_consecutive_waits",
            consecutive_waits=counters.get("consecutive_waits", 0),
            max_consecutive_waits=limits["max_consecutive_waits"],
        )
        return route_request_human(
            exp_dir,
            state_name,
            state_dir,
            judgments,
            "wait_limit_reached",
            f"consecutive wait limit reached before {reason_key}",
            context={"wait_reason": reason_key, "safety_counters": counters},
        )
    if limits["max_total_waits"] is not None and next_total > limits["max_total_waits"]:
        add(
            judgments,
            "wait_limit",
            False,
            "next wait would exceed max_total_waits",
            total_waits=counters.get("total_waits", 0),
            max_total_waits=limits["max_total_waits"],
        )
        return route_request_human(
            exp_dir,
            state_name,
            state_dir,
            judgments,
            "wait_limit_reached",
            f"total wait limit reached before {reason_key}",
            context={"wait_reason": reason_key, "safety_counters": counters},
        )

    action = wait_action(reason_key, wait_seconds)
    return route(
        exp_dir,
        state_name,
        state_dir,
        "wait",
        message,
        judgments,
        agent_required=False,
        suggested_action=action,
        commands=[command_for_action(action)],
    )


def decide(exp_dir, wait_seconds=WAIT_SECONDS):
    state_name = current_state_name(exp_dir)
    state_dir = exp_dir / state_name
    capture_path = state_dir / "00_capture.jpg"
    parsed_path = state_dir / "01_parsed_state.md"
    action_path = state_dir / "02_action.md"
    judgments = []

    if not capture_path.exists():
        add(judgments, "capture_exists", False, "current state has no capture image")
        return route(
            exp_dir,
            state_name,
            state_dir,
            "capture",
            "capture the current state image",
            judgments,
            agent_required=False,
            commands=["python3 capture.py --output s_current/00_capture.jpg"],
        )
    add(judgments, "capture_exists", True, "00_capture.jpg exists")

    if not parsed_path.exists():
        add(judgments, "parsed_state_exists", False, "current state has no parsed state markdown")
        return route(
            exp_dir,
            state_name,
            state_dir,
            "visual_parse",
            "run visual parsing and write 01_parsed_state.md",
            judgments,
            agent_required=True,
            required_agent_task="visual_parse",
            write="01_parsed_state.md",
        )
    add(judgments, "parsed_state_exists", True, "01_parsed_state.md exists")

    if action_path.exists():
        action, action_error = read_markdown_json(
            action_path,
            lambda value: isinstance(value, dict) and "action" in value,
        )
        if action_error:
            add(judgments, "action_file_valid", False, action_error)
            return route(
                exp_dir,
                state_name,
                state_dir,
                "repair_action_file",
                "02_action.md exists but does not contain a valid action JSON block",
                judgments,
                agent_required=True,
                required_agent_task="repair_or_confirm_action_file",
            )
        add(judgments, "action_file_valid", True, "02_action.md contains an action JSON block")
        if action.get("action") == "stop":
            return route(
                exp_dir,
                state_name,
                state_dir,
                "stopped",
                "current action is stop",
                judgments,
                agent_required=False,
                commands=[],
                action=action,
            )
        if action.get("action") == "request_human":
            sequence, sequence_error = read_json(exp_dir / "action_sequence.json")
            context = {"action": action}
            if sequence_error:
                add(judgments, "action_sequence_valid", False, sequence_error)
            else:
                add(judgments, "human_pause", True, "request_human action blocks automatic state advance")
                context.update(
                    {
                        "current_step": sequence.get("current_step"),
                        "last_error": sequence.get("last_error"),
                        "resume_options": sequence.get("resume_options", []),
                    }
                )
            return route(
                exp_dir,
                state_name,
                state_dir,
                "human_pause",
                "request_human is waiting for explicit human confirmation before the next state",
                judgments,
                agent_required=True,
                required_agent_task="wait_for_human_confirmation",
                commands_after_human=command_for_begin_next(state_name),
                context=context,
            )
        return route(
            exp_dir,
            state_name,
            state_dir,
            "begin_next",
            "current state already has an action; create and capture the next state",
            judgments,
            agent_required=False,
            commands=command_for_begin_next(state_name),
            action=action,
        )

    parsed, parsed_error = read_markdown_json(
        parsed_path,
        lambda value: isinstance(value, dict) and isinstance(value.get("table"), dict),
    )
    if parsed_error:
        add(judgments, "parsed_state_valid", False, parsed_error)
        return route(
            exp_dir,
            state_name,
            state_dir,
            "repair_parsed_state",
            "parsed state markdown must contain one JSON object with a table object",
            judgments,
            agent_required=True,
            required_agent_task="repair_parsed_state",
        )
    add(judgments, "parsed_state_valid", True, "parsed state JSON has a table object")

    sequence, sequence_error = read_json(exp_dir / "action_sequence.json")
    hole_cache, hole_error = read_json(exp_dir / "hole_card_cache.json")
    if sequence_error:
        add(judgments, "action_sequence_valid", False, sequence_error)
    else:
        add(judgments, "action_sequence_valid", True, "action_sequence.json loaded")
    if hole_error:
        add(judgments, "hole_card_cache_valid", False, hole_error)
    else:
        add(judgments, "hole_card_cache_valid", True, "hole_card_cache.json loaded")
    if sequence_error or hole_error:
        return route(
            exp_dir,
            state_name,
            state_dir,
            "repair_caches",
            "required cache files are missing or invalid",
            judgments,
            agent_required=True,
            required_agent_task="repair_cache_files",
        )
    safety_limits = loop_safety_limits(load_config(exp_dir / "config.yaml"))

    table = parsed["table"]
    loop_stage = parsed.get("loop_stage")
    if not loop_stage:
        loop_stage = sequence.get("loop_stage", "idle")
        add(judgments, "loop_stage_source", "fallback", "loop_stage missing in parsed state; using action_sequence.json")
    else:
        add(judgments, "loop_stage_source", "parsed_state", "loop_stage read from parsed state")
    if loop_stage not in STAGE_SET:
        add(judgments, "loop_stage_valid", False, f"unknown loop_stage: {loop_stage}")
        return route(
            exp_dir,
            state_name,
            state_dir,
            "invalid_stage",
            f"unknown loop_stage: {loop_stage}",
            judgments,
            agent_required=True,
            required_agent_task="repair_loop_stage",
            context={"loop_stage": loop_stage},
        )
    add(judgments, "loop_stage_valid", True, f"loop_stage is {loop_stage}")

    missing = table_missing_fields(table, loop_stage)
    if missing:
        add(
            judgments,
            "table_required_fields",
            False,
            f"table is missing fields required for loop_stage {loop_stage}",
            missing_fields=missing,
        )
        return route(
            exp_dir,
            state_name,
            state_dir,
            "repair_parsed_state",
            f"parsed table is missing fields required for loop_stage {loop_stage}",
            judgments,
            agent_required=True,
            required_agent_task="complete_parsed_state",
            missing_fields=missing,
            context={"loop_stage": loop_stage},
        )
    add(judgments, "table_required_fields", True, f"table has fields required for loop_stage {loop_stage}")

    scene_stable = table.get("scene_stable")
    is_my_turn = table.get("is_my_turn")
    fields_uncertain = uncertain_fields(table)

    if loop_stage == "down":
        add(judgments, "down_recovery", "agent_required", "down recovery requires image and safety judgment")
        return route(
            exp_dir,
            state_name,
            state_dir,
            "recover_down",
            "inspect recent states and cached sequence; choose retry, wait, or human help",
            judgments,
            agent_required=True,
            required_agent_task="recover_down",
            context={
                "current_step": sequence.get("current_step"),
                "last_error": sequence.get("last_error"),
                "human_required": sequence.get("human_required", False),
                "intent": sequence.get("intent"),
            },
        )

    if loop_stage == "to_recover":
        add(judgments, "retryable_recovery", "agent_required", "parsed state marks a recoverable physical no-op or harmless failure")
        if scene_stable is False:
            add(judgments, "to_recover_wait", "wait", "retryable recovery is marked, but the scene is not stable yet")
            return route_wait(
                exp_dir,
                state_name,
                state_dir,
                judgments,
                "to_recover_scene_unstable",
                "retryable recovery needs a stable scene before retry",
                wait_seconds,
                sequence=sequence,
                limits=safety_limits,
            )
        if scene_stable is not True:
            add(judgments, "to_recover_scene_stability", "unknown", "retryable recovery needs a clear scene_stable true value")
            return route(
                exp_dir,
                state_name,
                state_dir,
                "resolve_scene_stability",
                "retryable recovery needs scene stability to be confirmed before retry",
                judgments,
                agent_required=True,
                required_agent_task="resolve_scene_stability",
            )
        current_step = sequence.get("current_step") or first_pending_step(sequence)
        counters = safety_counters(sequence)
        retry_count = int(sequence.get("retry_count", 0))
        total_recoveries = int(counters.get("total_recoveries", 0))
        if safety_limits["max_step_retries"] is not None and retry_count >= safety_limits["max_step_retries"]:
            add(
                judgments,
                "retry_limit",
                False,
                "current sequence reached max_step_retries",
                retry_count=retry_count,
                max_step_retries=safety_limits["max_step_retries"],
            )
            return route_request_human(
                exp_dir,
                state_name,
                state_dir,
                judgments,
                "retry_limit_reached",
                "retry limit reached for the current action sequence",
                context={"current_step": current_step, "safety_counters": counters},
            )
        if safety_limits["max_total_recoveries"] is not None and total_recoveries >= safety_limits["max_total_recoveries"]:
            add(
                judgments,
                "retry_limit",
                False,
                "experiment reached max_total_recoveries",
                total_recoveries=total_recoveries,
                max_total_recoveries=safety_limits["max_total_recoveries"],
            )
            return route_request_human(
                exp_dir,
                state_name,
                state_dir,
                judgments,
                "retry_limit_reached",
                "total recovery limit reached for this experiment",
                context={"current_step": current_step, "safety_counters": counters},
            )
        if has_cached_command_step(sequence, current_step):
            return route(
                exp_dir,
                state_name,
                state_dir,
                "recover_retryable",
                "prepare and retry the cached atom command for the recoverable failure",
                judgments,
                agent_required=False,
                commands=[
                    (
                        f"python3 state.py prepare-retry --step {shlex.quote(current_step)} "
                        f"--reason to_recover --max-retries {safety_limits['max_step_retries']} "
                        f"--max-total-recoveries {safety_limits['max_total_recoveries']}"
                    ),
                    "python3 executor.py --continue-current",
                ],
                context={
                    "current_step": current_step,
                    "last_error": sequence.get("last_error"),
                    "intent": sequence.get("intent"),
                    "retry_count": sequence.get("retry_count", 0),
                },
            )
        return route(
            exp_dir,
            state_name,
            state_dir,
            "recover_retryable",
            "use the cached sequence plan to retry or repair the current embodied action",
            judgments,
            agent_required=True,
            required_agent_task="recover_retryable_action",
            context={
                "current_step": current_step,
                "last_error": sequence.get("last_error"),
                "intent": sequence.get("intent"),
                "action": sequence.get("action"),
                "plan": sequence.get("plan"),
                "steps": sequence.get("steps", []),
            },
        )

    if loop_stage == "lose":
        add(judgments, "lose", "agent_required", "parsed state marks the robot as losing the hand")
        return route(
            exp_dir,
            state_name,
            state_dir,
            "hand_lost",
            "do not pull chips back; decide whether to wait, stop, or prepare the next hand",
            judgments,
            agent_required=True,
            required_agent_task="handle_lost_hand",
            context={"table": table},
        )

    if scene_stable is False:
        add(judgments, "scene_stable", False, "parsed state marks the scene unstable")
        return route_wait(
            exp_dir,
            state_name,
            state_dir,
            judgments,
            "scene_unstable",
            "scene is unstable; wait and preserve the current sequence",
            wait_seconds,
            sequence=sequence,
            limits=safety_limits,
        )
    if scene_stable is not True:
        add(judgments, "scene_stable", "unknown", "scene_stable is not a clear true/false value")
        if loop_stage == "acting":
            return route_wait(
                exp_dir,
                state_name,
                state_dir,
                judgments,
                "robot_acting",
                "robot is acting and scene stability is unclear; wait before re-parsing",
                wait_seconds,
                sequence=sequence,
                limits=safety_limits,
            )
        return route(
            exp_dir,
            state_name,
            state_dir,
            "resolve_scene_stability",
            "scene stability must be judged before robot movement",
            judgments,
            agent_required=True,
            required_agent_task="resolve_scene_stability",
        )
    add(judgments, "scene_stable", True, "scene is stable")

    if loop_stage == "acting":
        add(judgments, "acting_sequence", "wait", "robot may still be moving or settling")
        return route_wait(
            exp_dir,
            state_name,
            state_dir,
            judgments,
            "robot_acting",
            "robot action may still be moving or settling",
            wait_seconds,
            sequence=sequence,
            limits=safety_limits,
        )

    if loop_stage == "show_hand":
        add(judgments, "show_hand", "agent_required", "opponent has shown cards or showdown requires revealing the robot hand")
        return route(
            exp_dir,
            state_name,
            state_dir,
            "show_hand",
            "reveal robot hole cards as needed, then compare showdown outcome",
            judgments,
            agent_required=True,
            required_agent_task="show_hand_or_resolve_showdown",
            suggested_actions=[
                {"action": "show_card", "position": "left"},
                {"action": "show_card", "position": "right"},
            ],
            context={
                "table": table,
                "hole_cards": {
                    "left": hole_cache.get("left"),
                    "right": hole_cache.get("right"),
                },
                "sequence": {
                    "intent": sequence.get("intent"),
                    "current_step": sequence.get("current_step"),
                },
            },
        )

    if loop_stage == "win":
        blockers = collection_uncertain_fields(fields_uncertain)
        if blockers:
            add(judgments, "collection_counts", "uncertain", "win is parsed, but chip or bet counts are uncertain", uncertain_fields=blockers)
            return route(
                exp_dir,
                state_name,
                state_dir,
                "resolve_collection_counts",
                "resolve bet/chip counts before pulling back winnings",
                judgments,
                agent_required=True,
                required_agent_task="resolve_collection_counts",
                context={"uncertain_fields": blockers},
            )
        action = {"action": "collect_winnings"}
        add(judgments, "win_collect", "collect_winnings", "parsed state marks the robot as the hand winner")
        return route(
            exp_dir,
            state_name,
            state_dir,
            "collect_winnings",
            "robot won the hand; pull back recognized bet chips",
            judgments,
            agent_required=False,
            suggested_action=action,
            commands=[command_for_action(action)],
            context={"table": table},
        )

    if loop_stage == "atom_idle":
        current_step = sequence.get("current_step") or first_pending_step(sequence)
        current_status = step_status(sequence, current_step) if current_step else None
        intent = sequence.get("intent")
        slot = view_slot_from_intent(intent)
        add(
            judgments,
            "atom_sequence",
            "open",
            "sequence has settled after an atom action",
            current_step=current_step,
            current_step_status=current_status,
            intent=intent,
        )
        if current_status == "dispatched":
            return route(
                exp_dir,
                state_name,
                state_dir,
                "verify_dispatched_step",
                "visually verify the dispatched atom before completing it in the cache",
                judgments,
                agent_required=True,
                required_agent_task="verify_dispatched_step_result",
                commands_after_verification=[f"python3 state.py complete-step --step {shlex.quote(current_step)}"],
                context={
                    "current_step": current_step,
                    "intent": intent,
                    "action": sequence.get("action"),
                    "plan": sequence.get("plan"),
                },
            )
        if current_step == "read_card":
            return route(
                exp_dir,
                state_name,
                state_dir,
                "read_held_card",
                "card-view sequence is waiting for held-card recognition",
                judgments,
                agent_required=True,
                required_agent_task="read_held_card",
                context={"slot": slot, "intent": intent},
            )
        if current_step == "put_down_card_face_up":
            if not slot:
                return route(
                    exp_dir,
                    state_name,
                    state_dir,
                    "repair_sequence",
                    "put_down_card_face_up is pending but the sequence intent does not identify left/right slot",
                    judgments,
                    agent_required=True,
                    required_agent_task="repair_action_sequence",
                    context={"current_step": current_step, "intent": intent},
                )
            action = {"action": "put_down_card", "position": slot, "face_up": True}
            return route(
                exp_dir,
                state_name,
                state_dir,
                "continue_sequence",
                "show-card sequence should return the held card face-up",
                judgments,
                agent_required=False,
                suggested_action=action,
                commands=[command_for_action(action)],
            )
        if current_step == "put_down_card":
            if not slot:
                return route(
                    exp_dir,
                    state_name,
                    state_dir,
                    "repair_sequence",
                    "put_down_card is pending but the sequence intent does not identify left/right slot",
                    judgments,
                    agent_required=True,
                    required_agent_task="repair_action_sequence",
                    context={"current_step": current_step, "intent": intent},
                )
            if not cached_card(hole_cache, slot):
                return route(
                    exp_dir,
                    state_name,
                    state_dir,
                    "cache_card_before_putdown",
                    "viewed card is not cached; read/cache it or request human help before put_down_card",
                    judgments,
                    agent_required=True,
                    required_agent_task="cache_held_card_or_request_human",
                    context={"slot": slot, "cache_entry": hole_cache.get(slot)},
                )
            action = {"action": "put_down_card", "position": slot, "face_up": False}
            return route(
                exp_dir,
                state_name,
                state_dir,
                "continue_sequence",
                "cached viewed card should be returned face-down",
                judgments,
                agent_required=False,
                suggested_action=action,
                commands=[command_for_action(action)],
            )
        if current_step == "verify_idle" or current_step is None:
            return route(
                exp_dir,
                state_name,
                state_dir,
                "verify_sequence_complete",
                "verify the full embodied sequence is complete before marking idle",
                judgments,
                agent_required=True,
                required_agent_task="verify_sequence_complete",
                commands_after_verification=["python3 state.py complete-action --loop-stage idle"],
                context={"current_step": current_step, "intent": intent},
            )
        if current_status == "pending" and has_cached_command_step(sequence, current_step):
            return route(
                exp_dir,
                state_name,
                state_dir,
                "continue_cached_command",
                "dispatch the next pending atom command from the cached action sequence",
                judgments,
                agent_required=False,
                commands=["python3 executor.py --continue-current"],
                context={"current_step": current_step, "intent": intent},
            )
        return route(
            exp_dir,
            state_name,
            state_dir,
            "verify_or_continue_sequence",
            "atom action is settled but the current sequence step needs agent judgment",
            judgments,
            agent_required=True,
            required_agent_task="verify_or_continue_sequence",
            context={"current_step": current_step, "intent": intent},
        )

    if loop_stage != "idle":
        add(judgments, "loop_stage_idle", False, f"unexpected loop_stage after validation: {loop_stage}")
        return route(
            exp_dir,
            state_name,
            state_dir,
            "invalid_stage",
            f"unexpected loop_stage: {loop_stage}",
            judgments,
            agent_required=True,
            required_agent_task="repair_loop_stage",
        )

    if is_my_turn is False:
        add(judgments, "is_my_turn", False, "turn marker indicates it is not the robot's turn")
        return route_wait(
            exp_dir,
            state_name,
            state_dir,
            judgments,
            "not_my_turn",
            "it is not the robot's turn",
            wait_seconds,
            sequence=sequence,
            limits=safety_limits,
        )
    if is_my_turn is not True:
        add(judgments, "is_my_turn", "unknown", "is_my_turn is not a clear true/false value")
        return route(
            exp_dir,
            state_name,
            state_dir,
            "resolve_turn",
            "turn marker must be judged before view-card or poker action",
            judgments,
            agent_required=True,
            required_agent_task="resolve_turn",
        )
    add(judgments, "is_my_turn", True, "turn marker indicates the robot's turn")

    slot = next_unknown_hole(hole_cache)
    if slot:
        add(judgments, "hole_cards_cached", False, f"{slot} hole card is missing from cache")
        action = {"action": "view_card", "position": slot}
        return route(
            exp_dir,
            state_name,
            state_dir,
            "view_hole_card",
            f"{slot} hole card is not cached",
            judgments,
            agent_required=False,
            suggested_action=action,
            commands=[command_for_action(action)],
        )
    add(judgments, "hole_cards_cached", True, "left and right hole cards are cached")

    if fields_uncertain:
        add(judgments, "uncertain_fields", False, "parsed state has uncertain fields", uncertain_fields=fields_uncertain)
        return route(
            exp_dir,
            state_name,
            state_dir,
            "resolve_uncertain_fields",
            "resolve uncertain parsed fields before poker action selection",
            judgments,
            agent_required=True,
            required_agent_task="resolve_uncertain_fields",
            context={"uncertain_fields": fields_uncertain},
        )
    add(judgments, "uncertain_fields", True, "no uncertain fields")

    return route(
        exp_dir,
        state_name,
        state_dir,
        "choose_poker_action",
        "state is idle, stable, robot turn, and hole cards are cached",
        judgments,
        agent_required=True,
        required_agent_task="choose_poker_action",
        context={
            "table": table,
            "hole_cards": {
                "left": hole_cache.get("left"),
                "right": hole_cache.get("right"),
            },
        },
    )


def main():
    parser = argparse.ArgumentParser(description="Route the current DexHoldem V2 state.")
    parser.add_argument("--exp-dir")
    parser.add_argument("--wait-seconds", type=float, default=WAIT_SECONDS)
    args = parser.parse_args()
    try:
        print(json.dumps(decide(resolve_exp_dir(args.exp_dir), wait_seconds=args.wait_seconds), indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
