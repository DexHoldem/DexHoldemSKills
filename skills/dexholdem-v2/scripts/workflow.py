#!/usr/bin/env python3
"""Deterministic DexHoldem per-state workflow gate.

This helper does not parse images and does not choose poker strategy. It only
checks the state-folder contract and returns the next mechanical gate for the
coding agent.
"""

import argparse
import json
import re
from pathlib import Path


WAIT_SECONDS = 3


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with path.open("r") as f:
        return json.load(f)


def extract_json_blocks(markdown):
    blocks = []
    for block in re.findall(r"```json\s*(.*?)```", markdown, flags=re.S):
        try:
            blocks.append(json.loads(block))
        except json.JSONDecodeError:
            pass
    return blocks


def read_markdown_json(path, predicate=None):
    path = Path(path)
    if not path.exists():
        return None
    for block in extract_json_blocks(path.read_text()):
        if predicate is None or predicate(block):
            return block
    return None


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


def current_state_name(exp_dir):
    link = exp_dir / "s_current"
    if link.exists():
        return link.resolve().name
    states = sorted([p.name for p in exp_dir.glob("s[0-9]*") if p.is_dir()], key=lambda x: int(x[1:]))
    if not states:
        raise RuntimeError("no state folders found")
    return states[-1]


def command_for_action(action):
    encoded = json.dumps(action, separators=(",", ":"))
    return f"python3 executor.py --action '{encoded}'"


def done_action(action_path):
    action = read_markdown_json(action_path, lambda value: isinstance(value, dict) and "action" in value)
    return action if isinstance(action, dict) else None


def next_unknown_hole(cache):
    for slot in ("left", "right"):
        item = cache.get(slot, {}) if isinstance(cache, dict) else {}
        if item.get("status") != "cached" or not item.get("card"):
            return slot
    return None


def view_slot_from_intent(intent):
    if intent == "view_left_hole_card":
        return "left"
    if intent == "view_right_hole_card":
        return "right"
    if intent == "show_left_hole_card":
        return "left"
    if intent == "show_right_hole_card":
        return "right"
    return None


def response(exp_dir, state_name, state_dir, next_step, reason, **extra):
    data = {
        "exp_dir": str(exp_dir),
        "state": state_name,
        "state_dir": str(state_dir),
        "next_step": next_step,
        "reason": reason,
    }
    data.update(extra)
    return data


def decide(exp_dir):
    state_name = current_state_name(exp_dir)
    state_dir = exp_dir / state_name
    capture = state_dir / "00_capture.jpg"
    parsed_path = state_dir / "01_parsed_state.md"
    action_path = state_dir / "02_action.md"

    if not capture.exists():
        return response(
            exp_dir,
            state_name,
            state_dir,
            "capture",
            "current state has no capture image",
            agent_required=False,
            commands=["python3 capture.py --output s_current/00_capture.jpg"],
        )

    if not parsed_path.exists():
        return response(
            exp_dir,
            state_name,
            state_dir,
            "visual_parse",
            "current state has no parsed state markdown",
            agent_required=True,
            write="01_parsed_state.md",
        )

    if action_path.exists():
        action = done_action(action_path)
        if action and action.get("action") == "stop":
            return response(
                exp_dir,
                state_name,
                state_dir,
                "stopped",
                "current action is stop",
                agent_required=False,
                commands=[],
            )
        return response(
            exp_dir,
            state_name,
            state_dir,
            "begin_next",
            "current state already has an action file",
            agent_required=False,
            commands=[
                f"python3 state.py begin-next --after {state_name}",
                "python3 capture.py --output s_current/00_capture.jpg",
            ],
        )

    parsed = read_markdown_json(parsed_path, lambda value: isinstance(value, dict) and "table" in value)
    sequence = read_json(exp_dir / "action_sequence.json", {}) or {}
    hole_cache = read_json(exp_dir / "hole_card_cache.json", {}) or {}
    table = parsed.get("table", {}) if isinstance(parsed, dict) else {}
    loop_stage = parsed.get("loop_stage") if isinstance(parsed, dict) else None
    loop_stage = loop_stage or sequence.get("loop_stage", "idle")

    if loop_stage == "down":
        return response(
            exp_dir,
            state_name,
            state_dir,
            "recover_down",
            "current loop stage is down",
            agent_required=True,
            context={"current_step": sequence.get("current_step"), "last_error": sequence.get("last_error")},
        )

    if loop_stage == "to_recover":
        if table.get("scene_stable") is False:
            action = {"action": "wait", "reason": "to_recover_scene_unstable", "sleep_seconds": WAIT_SECONDS}
            return response(
                exp_dir,
                state_name,
                state_dir,
                "wait",
                "retryable recovery needs a stable scene before retry",
                agent_required=False,
                suggested_action=action,
                commands=[command_for_action(action)],
            )
        return response(
            exp_dir,
            state_name,
            state_dir,
            "recover_retryable",
            "current loop stage is to_recover",
            agent_required=True,
            context={
                "current_step": sequence.get("current_step"),
                "last_error": sequence.get("last_error"),
                "intent": sequence.get("intent"),
                "action": sequence.get("action"),
                "plan": sequence.get("plan"),
            },
        )

    if loop_stage == "acting":
        action = {"action": "wait", "reason": "robot_acting", "sleep_seconds": WAIT_SECONDS}
        return response(
            exp_dir,
            state_name,
            state_dir,
            "wait",
            "robot action may still be moving or settling",
            agent_required=False,
            suggested_action=action,
            commands=[command_for_action(action)],
        )

    if loop_stage == "lose":
        return response(
            exp_dir,
            state_name,
            state_dir,
            "hand_lost",
            "robot lost the hand; do not pull chips back",
            agent_required=True,
            context={"table": table},
        )

    if table.get("scene_stable") is False:
        action = {"action": "wait", "reason": "scene_unstable", "sleep_seconds": WAIT_SECONDS}
        return response(
            exp_dir,
            state_name,
            state_dir,
            "wait",
            "scene is marked unstable",
            agent_required=False,
            suggested_action=action,
            commands=[command_for_action(action)],
        )

    if loop_stage == "show_hand":
        return response(
            exp_dir,
            state_name,
            state_dir,
            "show_hand",
            "opponent has shown cards or showdown requires revealing the robot hand",
            agent_required=True,
            suggested_actions=[
                {"action": "show_card", "position": "left"},
                {"action": "show_card", "position": "right"},
            ],
            context={"table": table, "hole_cards": {"left": hole_cache.get("left"), "right": hole_cache.get("right")}},
        )

    if loop_stage == "win":
        action = {"action": "collect_winnings"}
        return response(
            exp_dir,
            state_name,
            state_dir,
            "collect_winnings",
            "robot won the hand; pull back recognized bet chips",
            agent_required=False,
            suggested_action=action,
            commands=[command_for_action(action)],
        )

    if loop_stage == "atom_idle":
        current_step = sequence.get("current_step")
        intent = sequence.get("intent")
        slot = view_slot_from_intent(intent)
        if current_step == "read_card":
            return response(
                exp_dir,
                state_name,
                state_dir,
                "read_held_card",
                "card-view sequence is waiting for held-card recognition",
                agent_required=True,
                context={"slot": slot, "intent": intent},
            )
        if current_step == "put_down_card_face_up" and slot:
            action = {"action": "put_down_card", "position": slot, "face_up": True}
            return response(
                exp_dir,
                state_name,
                state_dir,
                "continue_sequence",
                "show-card sequence should return the held card face-up",
                agent_required=False,
                suggested_action=action,
                commands=[command_for_action(action)],
            )
        if current_step == "put_down_card" and slot:
            action = {"action": "put_down_card", "position": slot, "face_up": False}
            return response(
                exp_dir,
                state_name,
                state_dir,
                "continue_sequence",
                "cached viewed card should be returned face-down",
                agent_required=False,
                suggested_action=action,
                commands=[command_for_action(action)],
            )
        return response(
            exp_dir,
            state_name,
            state_dir,
            "verify_or_continue_sequence",
            "atom action is settled but the action sequence still has pending steps",
            agent_required=True,
            context={"current_step": current_step, "intent": intent},
        )

    if loop_stage != "idle":
        return response(
            exp_dir,
            state_name,
            state_dir,
            "invalid_stage",
            f"unknown loop_stage: {loop_stage}",
            agent_required=True,
        )

    if table.get("is_my_turn") is False:
        action = {"action": "wait", "reason": "not_my_turn", "sleep_seconds": WAIT_SECONDS}
        return response(
            exp_dir,
            state_name,
            state_dir,
            "wait",
            "turn marker indicates it is not the robot's turn",
            agent_required=False,
            suggested_action=action,
            commands=[command_for_action(action)],
        )

    slot = next_unknown_hole(hole_cache)
    if slot:
        action = {"action": "view_card", "position": slot}
        return response(
            exp_dir,
            state_name,
            state_dir,
            "view_hole_card",
            f"{slot} hole card is not cached",
            agent_required=False,
            suggested_action=action,
            commands=[command_for_action(action)],
        )

    return response(
        exp_dir,
        state_name,
        state_dir,
        "choose_poker_action",
        "state is idle, stable, robot turn, and hole cards are cached",
        agent_required=True,
        context={"table": table, "hole_cards": {"left": hole_cache.get("left"), "right": hole_cache.get("right")}},
    )


def main():
    parser = argparse.ArgumentParser(description="Inspect the DexHoldem state timeline and return the next workflow gate.")
    parser.add_argument("--exp-dir")
    args = parser.parse_args()
    try:
        print(json.dumps(decide(resolve_exp_dir(args.exp_dir)), indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
