#!/usr/bin/env python3
"""Translate a poker decision (or special action) into a sequence of robot primitive commands."""

import argparse
import json
import sys


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
            # Check if there are unused chips of this denomination
            used = 0
            for r in result:
                if r["value"] == chip["value"]:
                    used = r["value"]  # not count, just flag
                    break
            available = chip["count"]
            for r in result:
                if r["value"] == chip["value"]:
                    available -= r["count"]
                    break
            if available > 0 and chip["value"] >= remaining:
                # Add one chip of this denomination
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
            # Still can't cover — use any available chip that's large enough
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


def translate(action_obj, my_chips=None):
    """Convert a poker action dict to a list of robot command dicts."""
    action = action_obj.get("action")

    if action == "view_card":
        return [
            {"command": "python3 play_audio.py wyyp.mp3", "local": True},
            {"command": "pick_up_card", "args": {}},
            {"command": "view_card", "args": {}},
            {"command": "put_down_card", "args": {}},
            {"command": "python3 play_audio.py pmywt.mp3", "local": True},
        ]

    if action == "fold":
        return [{"command": "fold_cards", "args": {}}]

    if action == "check":
        return [{"command": "tap_table", "args": {}}]

    if action == "call":
        bet_chips = action_obj.get("bet_chips", 0)
        if bet_chips <= 0:
            return []
        pick_args = {"amount": bet_chips}
        if my_chips is not None:
            pick_args["chips"] = split_chips(bet_chips, my_chips)
        return [
            {"command": "pick_chips", "args": pick_args},
            {"command": "place_bet", "args": {}},
        ]

    if action == "raise":
        bet_chips = action_obj.get("bet_chips")
        if bet_chips is None or bet_chips <= 0:
            print("Error: 'raise' requires a positive 'bet_chips' value", file=sys.stderr)
            sys.exit(1)
        pick_args = {"amount": bet_chips}
        if my_chips is not None:
            pick_args["chips"] = split_chips(bet_chips, my_chips)
        return [
            {"command": "pick_chips", "args": pick_args},
            {"command": "place_bet", "args": {}},
        ]

    if action == "all_in":
        return [{"command": "push_all_chips", "args": {}}]

    print(f"Error: unknown action '{action}'", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Translate a poker action into robot primitive commands."
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
        help='JSON string of chip inventory, e.g. \'[{"value": 100, "count": 4}, {"value": 10, "count": 2}]\'',
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

    commands = translate(action_obj, my_chips=my_chips)
    print(json.dumps(commands))


if __name__ == "__main__":
    main()
