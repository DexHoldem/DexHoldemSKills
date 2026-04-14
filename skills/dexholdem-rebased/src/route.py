#!/usr/bin/env python3
"""Route vision output to the next loop stage.

Reads game state JSON from vision, loads hand cache and execution state,
and outputs a routing decision: reason, resume, wait, or stop.

Usage:
    python3 src/route.py --state '<game_state_json>'

Output (JSON to stdout):
    {"next": "stop"}
    {"next": "wait", "reason": "between_hands"}
    {"next": "wait", "reason": "not_my_turn"}
    {"next": "wait", "reason": "robot_moving"}
    {"next": "resume"}
    {"next": "reason", "hand": ["Ks", "Qh"], "game_state": {...}}
    {"next": "reason", "action_hint": "view_card", "position": "left", "game_state": {...}}
"""

import argparse
import json
import os
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))


def _run_state_cmd(subcommand, *args):
    """Run an execution_state.py subcommand and return stdout."""
    cmd = [sys.executable, os.path.join(SRC_DIR, "execution_state.py"), subcommand] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=SKILL_DIR)
    return result.stdout.strip(), result.returncode


def _load_hand_cache():
    stdout, _ = _run_state_cmd("hand-load")
    if stdout:
        try:
            cache = json.loads(stdout)
            cache.setdefault("pending_putdown", None)
            return cache
        except json.JSONDecodeError:
            pass
    return {"left": None, "right": None, "pending_putdown": None}


def _load_execution_state():
    stdout, rc = _run_state_cmd("load")
    if rc != 0 or not stdout:
        return None
    try:
        state = json.loads(stdout)
        return state if state else None
    except json.JSONDecodeError:
        return None


def _cache_card(position, card):
    _run_state_cmd("hand-set", "--position", position, "--card", card)


def _clear_hand_cache():
    _run_state_cmd("hand-clear")


def route(game_state):
    """Decide the next loop action based on game state."""
    game_phase = game_state.get("game_phase", "active")
    is_my_turn = game_state.get("is_my_turn", False)
    robot_state = game_state.get("robot_state", "idle")
    held_card = game_state.get("held_card")

    # 1. Game over
    if game_phase == "game_over":
        return {"next": "stop"}

    # 2. Between hands — clear hand cache, wait for next deal
    if game_phase == "between_hands":
        _clear_hand_cache()
        return {"next": "wait", "reason": "between_hands"}

    # 3. Showdown or not my turn
    if game_phase == "showdown" or not is_my_turn:
        return {"next": "wait", "reason": "not_my_turn"}

    # 4. Interrupted execution — resume
    exec_state = _load_execution_state()
    if exec_state and exec_state.get("phase") in ("executing", "verifying"):
        return {"next": "resume"}

    # 5. Robot moving — wait for it to finish
    if robot_state == "moving":
        return {"next": "wait", "reason": "robot_moving"}

    hand_cache = _load_hand_cache()

    # 5a. Hard lock: a prior view_card set pending_putdown. The next round
    #     MUST put the card back down at that position — ignore vision and
    #     all other routing logic. This enforces the view→put_down pair.
    pending = hand_cache.get("pending_putdown")
    if pending in ("left", "right"):
        return {
            "next": "reason",
            "action_hint": "put_down_card",
            "position": pending,
            "game_state": game_state,
        }

    # 6. Robot holding a card — cache it, then wait (put_down will happen next iteration)

    if robot_state == "holding_card" and held_card:
        # Cache the card in the next empty position
        if hand_cache["left"] is None:
            _cache_card("left", held_card)
            hand_cache["left"] = held_card
            put_down_position = "left"
        elif hand_cache["right"] is None:
            _cache_card("right", held_card)
            hand_cache["right"] = held_card
            put_down_position = "right"
        else:
            put_down_position = "left"

        # If hand is now complete, reason; otherwise need to put card down first
        if hand_cache["left"] and hand_cache["right"]:
            return {
                "next": "reason",
                "hand": [hand_cache["left"], hand_cache["right"]],
                "game_state": game_state,
            }
        else:
            return {
                "next": "reason",
                "action_hint": "put_down_card",
                "position": put_down_position,
                "game_state": game_state,
            }

    # 7. Robot idle, hand incomplete — need to view cards
    if hand_cache["left"] is None:
        return {
            "next": "reason",
            "action_hint": "view_card",
            "position": "left",
            "game_state": game_state,
        }
    if hand_cache["right"] is None:
        return {
            "next": "reason",
            "action_hint": "view_card",
            "position": "right",
            "game_state": game_state,
        }

    # 8. Robot idle, hand complete, my turn — full reasoning
    return {
        "next": "reason",
        "hand": [hand_cache["left"], hand_cache["right"]],
        "game_state": game_state,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Route vision output to the next loop stage.",
        epilog="""
Output formats:
  {"next": "stop"}                                          Game over
  {"next": "wait", "reason": "..."}                         Wait and recapture
  {"next": "resume"}                                        Resume interrupted execution
  {"next": "reason", "hand": [...], "game_state": {...}}    Proceed to poker reasoning
  {"next": "reason", "action_hint": "view_card", ...}       View card before reasoning
  {"next": "reason", "action_hint": "put_down_card", ...}   Put card down first
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--state",
        required=True,
        help="Game state JSON string from vision model",
    )
    args = parser.parse_args()

    try:
        game_state = json.loads(args.state)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"invalid JSON: {e}"}), file=sys.stderr)
        sys.exit(1)

    result = route(game_state)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
