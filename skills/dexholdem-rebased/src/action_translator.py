#!/usr/bin/env python3
"""Translate a poker action into a robot command sequence with a pre-stage prefix.

Instruction table:
    0  — view left card          7  — pull back chip 10
    1  — view right card         8  — pull back chip 50
    2  — push chip 5  (bet)      9  — pull back chip 100
    3  — push chip 10 (bet)      10 — put down left  (face down)
    4  — push chip 50 (bet)      11 — put down right (face down)
    5  — push chip 100 (bet)     12 — put down left  (face up)
    6  — pull back chip 5        13 — put down right (face up)

Output format (JSON to stdout):
    {"prefix": "reset" | "ctrlc" | null, "commands": ["..."]}

The `prefix` declares what must run on the remote BEFORE dispatching the
commands list:
    - "reset" : send Ctrl+C, then click the reset-hand GUI button, then wait
                for the arm to settle at its init pose. Used whenever the
                next action needs a free hand.
    - "ctrlc" : send Ctrl+C only. Used for `put_down_card` (instr 10–13),
                because the arm is currently holding a card and a reset
                click would drop it.
    - null    : no-op (placeholder actions like check / fold).
"""

import argparse
import json
import sys

# ── instruction constants ────────────────────────────────────────────────

INSTR_VIEW_LEFT = 0
INSTR_VIEW_RIGHT = 1

INSTR_PUSH = {5: 2, 10: 3, 50: 4, 100: 5}
INSTR_PULL = {5: 6, 10: 7, 50: 8, 100: 9}

INSTR_PUT_DOWN = {
    ("left", False): 10, ("right", False): 11,   # face down
    ("left", True): 12,  ("right", True): 13,     # face up
}


# ── chip decomposition ───────────────────────────────────────────────────

def split_chips(amount, my_chips):
    """Decompose a bet amount into specific chips from the robot's inventory.

    Uses a greedy largest-first algorithm. If exact change isn't possible,
    overpays with one extra chip of the smallest denomination that covers
    the remainder (dealer makes change).

    Args:
        amount: int — total chips to bet
        my_chips: list of {"value": V, "count": N}

    Returns:
        list of {"value": V, "count": N} with only non-zero counts
    """
    sorted_chips = sorted(my_chips, key=lambda c: c["value"], reverse=True)
    result = []
    remaining = amount

    for chip in sorted_chips:
        if remaining <= 0:
            break
        use = min(chip["count"], remaining // chip["value"])
        if use > 0:
            result.append({"value": chip["value"], "count": use})
            remaining -= use * chip["value"]

    if remaining > 0:
        # No exact change — find smallest denomination that covers the remainder
        for chip in reversed(sorted_chips):
            available = chip["count"]
            for r in result:
                if r["value"] == chip["value"]:
                    available -= r["count"]
                    break
            if available > 0 and chip["value"] >= remaining:
                found = False
                for r in result:
                    if r["value"] == chip["value"]:
                        r["count"] += 1
                        found = True
                        break
                if not found:
                    result.append({"value": chip["value"], "count": 1})
                print(
                    f"Warning: no exact change for {amount}. "
                    f"Overpaying with extra {chip['value']} chip (dealer makes change).",
                    file=sys.stderr,
                )
                remaining = 0
                break

        if remaining > 0:
            for chip in sorted_chips:
                available = chip["count"]
                for r in result:
                    if r["value"] == chip["value"]:
                        available -= r["count"]
                        break
                if available > 0:
                    found = False
                    for r in result:
                        if r["value"] == chip["value"]:
                            r["count"] += 1
                            found = True
                            break
                    if not found:
                        result.append({"value": chip["value"], "count": 1})
                    print(
                        f"Warning: no exact change for {amount}. "
                        f"Overpaying with extra {chip['value']} chip (dealer makes change).",
                        file=sys.stderr,
                    )
                    remaining = 0
                    break

    return result


ROBOT_CMD = "python TexasPoker/robot_client.py --server_ip localhost --obs_horizon 1 --instruction {}"


def _instr_cmd(instr):
    """Format a single instruction integer as a robot_client.py command."""
    return ROBOT_CMD.format(instr)


def _chips_to_commands(chip_list):
    """Expand a split_chips result into a flat list of robot commands."""
    commands = []
    for entry in chip_list:
        instr = INSTR_PUSH.get(entry["value"])
        if instr is None:
            print(f"Warning: unknown chip value {entry['value']}, skipping", file=sys.stderr)
            continue
        commands.extend([_instr_cmd(instr)] * entry["count"])
    return commands


# ── translate ─────────────────────────────────────────────────────────────

def translate(action_obj, my_chips=None):
    """Convert a poker action dict to {prefix, commands}.

    `prefix` is one of "reset", "ctrlc", or None. See the module docstring.
    `commands` is a list of robot command strings (possibly empty).
    """
    action = action_obj.get("action")

    if action == "view_card":
        position = action_obj.get("position", "left")
        instr = INSTR_VIEW_LEFT if position == "left" else INSTR_VIEW_RIGHT
        return {"prefix": "reset", "commands": [_instr_cmd(instr)]}

    if action == "put_down_card":
        position = action_obj.get("position", "left")
        face_up = action_obj.get("face_up", False)
        instr = INSTR_PUT_DOWN.get((position, face_up))
        if instr is None:
            print(f"Error: invalid put_down_card position={position} face_up={face_up}", file=sys.stderr)
            sys.exit(1)
        # NOTE: no reset — the arm is holding a card. Reset would drop it.
        return {"prefix": "ctrlc", "commands": [_instr_cmd(instr)]}

    if action == "check":
        print("Warning: check is a placeholder — no instruction assigned yet", file=sys.stderr)
        return {"prefix": None, "commands": []}

    if action == "fold":
        print("Warning: fold is a placeholder — no instruction assigned yet", file=sys.stderr)
        return {"prefix": None, "commands": []}

    if action in ("call", "raise"):
        bet_chips = action_obj.get("bet_chips", 0)
        if bet_chips <= 0:
            return {"prefix": None, "commands": []}
        if my_chips is None:
            print("Error: call/raise requires --chips inventory", file=sys.stderr)
            sys.exit(1)
        chip_list = split_chips(bet_chips, my_chips)
        return {"prefix": "reset", "commands": _chips_to_commands(chip_list)}

    if action == "all_in":
        if my_chips is None:
            print("Error: all_in requires --chips inventory", file=sys.stderr)
            sys.exit(1)
        return {"prefix": "reset", "commands": _chips_to_commands(my_chips)}

    print(f"Error: unknown action '{action}'", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Translate a poker action into robot instruction integers."
    )
    parser.add_argument(
        "--action",
        required=True,
        help='JSON string, e.g. \'{"action": "call", "bet_chips": 50}\'',
    )
    parser.add_argument(
        "--chips",
        required=False,
        default=None,
        help='JSON string of chip inventory, e.g. \'[{"value": 100, "count": 4}]\'',
    )
    args = parser.parse_args()

    try:
        action_obj = json.loads(args.action)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)

    my_chips = None
    if args.chips is not None:
        try:
            my_chips = json.loads(args.chips)
        except json.JSONDecodeError as e:
            print(f"Error: invalid --chips JSON — {e}", file=sys.stderr)
            sys.exit(1)

    result = translate(action_obj, my_chips=my_chips)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
