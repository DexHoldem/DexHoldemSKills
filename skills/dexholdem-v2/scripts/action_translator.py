#!/usr/bin/env python3
"""Translate DexHoldem V2 action JSON into robot policy commands."""

import argparse
import json

from utils import STAGE_SET, STAGES, utc_now

INSTR_VIEW_LEFT = 0
INSTR_VIEW_RIGHT = 1
INSTR_PUSH = {5: 2, 10: 3, 50: 4, 100: 5}
INSTR_PULL = {5: 6, 10: 7, 50: 8, 100: 9}
INSTR_PUT_DOWN = {
    ("left", False): 10,
    ("right", False): 11,
    ("left", True): 12,
    ("right", True): 13,
}
ROBOT_CMD = "python Dexas-Policy/robot_client.py --instruction {} --port 13579 --server_ip 192.168.1.200"
DENOMINATIONS = tuple(sorted(INSTR_PUSH.keys()))


def _cmd(instr):
    return ROBOT_CMD.format(instr)


def normalize_chip_map(chips):
    if chips is None:
        return {}
    if isinstance(chips, dict):
        return {int(k): int(v) for k, v in chips.items()}
    if isinstance(chips, list):
        result = {}
        for item in chips:
            result[int(item["value"])] = int(item["count"])
        return result
    raise ValueError("chips must be a denomination map or list")


def chip_total(chips):
    normalized = normalize_chip_map(chips)
    return sum(int(value) * int(count) for value, count in normalized.items())


def add_chip_maps(*chip_maps):
    result = {}
    for chip_map in chip_maps:
        for value, count in normalize_chip_map(chip_map).items():
            result[int(value)] = result.get(int(value), 0) + int(count)
    return {value: count for value, count in result.items() if count > 0}


def merge_table(action, table):
    merged = {}
    if isinstance(table, dict):
        merged.update(table)
    action_table = action.get("table")
    if isinstance(action_table, dict):
        merged.update(action_table)
    return merged


def resolve_chip_inventory(action, chips, table):
    if chips is not None:
        return chips
    if action.get("chips") is not None:
        return action.get("chips")
    return table.get("my_chips")


def resolve_chip_field(action, table, field):
    if action.get(field) is not None:
        return action.get(field)
    if table.get(field) is not None:
        return table.get(field)
    raise ValueError(f"{field} is required")


def compute_call_amount(action, table):
    if action.get("bet_chips") is not None:
        return int(action["bet_chips"]), {"source": "action.bet_chips_override"}
    my_current_bet = resolve_chip_field(action, table, "my_current_bet")
    opponent_bet = resolve_chip_field(action, table, "opponent_bet")
    my_total = chip_total(my_current_bet)
    opponent_total = chip_total(opponent_bet)
    return max(0, opponent_total - my_total), {
        "source": "opponent_bet_minus_my_current_bet",
        "my_current_bet_total": my_total,
        "opponent_bet_total": opponent_total,
    }


def compute_raise_amount(action, table):
    if action.get("bet_chips") is not None:
        return int(action["bet_chips"]), {"source": "action.bet_chips_override"}
    if action.get("amount") is None:
        raise ValueError("raise requires amount when bet_chips override is absent")
    my_current_bet = resolve_chip_field(action, table, "my_current_bet")
    my_total = chip_total(my_current_bet)
    raise_to_total = int(action["amount"])
    return max(0, raise_to_total - my_total), {
        "source": "raise_amount_minus_my_current_bet",
        "raise_to_total": raise_to_total,
        "my_current_bet_total": my_total,
    }


def compute_collect_sources(action, table):
    for field in ("chip_counts", "pull_chip_counts"):
        if action.get(field) is not None:
            counts = normalize_chip_map(action[field])
            return [{"source": "unspecified_winnings", "chip_counts": counts}], {
                "source": f"action.{field}",
                "physical_collect_chips": chip_total(counts),
            }

    my_current_bet = table.get("my_current_bet")
    opponent_bet = table.get("opponent_bet")
    if my_current_bet is None or opponent_bet is None:
        raise ValueError("collect_winnings requires chip_counts or table my_current_bet/opponent_bet")

    my_counts = normalize_chip_map(my_current_bet)
    opponent_counts = normalize_chip_map(opponent_bet)
    counts = add_chip_maps(my_counts, opponent_counts)
    return [
        {"source": "opponent_bet", "chip_counts": opponent_counts},
        {"source": "my_current_bet", "chip_counts": my_counts},
    ], {
        "source": "my_current_bet_plus_opponent_bet_by_zone",
        "my_current_bet_total": chip_total(my_counts),
        "opponent_bet_total": chip_total(opponent_counts),
        "physical_collect_chips": chip_total(counts),
    }


def split_chips_exact(amount, chips):
    inventory = normalize_chip_map(chips)
    target = int(amount)
    if target < 0:
        raise ValueError(f"chip amount must be non-negative: {amount}")
    if target == 0:
        return {}

    best_counts = None
    best_key = None

    def search(index, remaining, counts):
        nonlocal best_counts, best_key
        if index == len(DENOMINATIONS):
            if remaining == 0:
                key = (
                    sum(counts.values()),
                    tuple(-int(value) for value in sorted(counts.keys(), reverse=True) for _ in range(counts[value])),
                )
                if best_key is None or key < best_key:
                    best_key = key
                    best_counts = {value: count for value, count in counts.items() if count > 0}
            return

        value = sorted(DENOMINATIONS, reverse=True)[index]
        max_count = min(int(inventory.get(value, 0)), remaining // value)
        for count in range(max_count, -1, -1):
            if count:
                counts[value] = count
            else:
                counts.pop(value, None)
            search(index + 1, remaining - value * count, counts)
        counts.pop(value, None)

    search(0, target, {})
    if best_counts is None:
        available_total = chip_total(inventory)
        raise ValueError(
            f"cannot make exact chip amount {target} from available chips {dict(sorted(inventory.items()))}; "
            f"available total is {available_total}"
        )
    return best_counts


def chip_commands_and_steps(chip_counts, instruction_map=INSTR_PUSH, verb="push"):
    commands = []
    steps = []
    for value in sorted(chip_counts.keys(), reverse=True):
        instr = instruction_map.get(int(value))
        if instr is None:
            raise ValueError(f"unsupported chip denomination {value}")
        for index in range(int(chip_counts[value])):
            commands.append(_cmd(instr))
            steps.append(f"{verb}_chip_{int(value)}_{index + 1}")
    return commands, steps


def intent_for_action(action):
    name = action.get("action", "unknown")
    if name == "view_card":
        return f"view_{action.get('position', 'left')}_hole_card"
    if name == "show_card":
        return f"show_{action.get('position', 'left')}_hole_card"
    if name == "pull_back_chips":
        return "collect_winnings"
    return name


def parse_translation_as_sequence_cache(action, translation, sequence_id=None, loop_stage="acting"):
    if loop_stage not in STAGE_SET:
        raise ValueError(f"invalid loop stage: {loop_stage}")
    steps = [{"name": step, "status": "pending"} for step in translation.get("sequence_steps", [])]
    return {
        "schema_version": 1,
        "sequence_id": sequence_id,
        "loop_stage": loop_stage,
        "intent": intent_for_action(action),
        "action": action,
        "plan": translation,
        "steps": steps,
        "current_step": steps[0]["name"] if steps else None,
        "retry_count": 0,
        "last_error": None,
        "human_required": False,
        "updated_at": utc_now(),
    }


def translate(action, chips=None, table=None):
    name = action.get("action")
    table = merge_table(action, table)

    if name == "wait":
        return {"prefix": None, "commands": [], "command_steps": [], "sequence_steps": []}

    if name in ("request_human", "stop"):
        return {"prefix": None, "commands": [], "command_steps": [], "sequence_steps": [name]}

    if name == "view_card":
        position = action.get("position", "left")
        instr = INSTR_VIEW_LEFT if position == "left" else INSTR_VIEW_RIGHT
        return {
            "prefix": "reset",
            "commands": [_cmd(instr)],
            "command_steps": ["pick_card"],
            "sequence_steps": ["pick_card", "read_card", "put_down_card", "verify_idle"],
        }

    if name == "show_card":
        position = action.get("position", "left")
        if position not in ("left", "right"):
            raise ValueError(f"invalid show_card position={position}")
        instr = INSTR_VIEW_LEFT if position == "left" else INSTR_VIEW_RIGHT
        return {
            "prefix": "reset",
            "commands": [_cmd(instr)],
            "command_steps": ["pick_card"],
            "sequence_steps": ["pick_card", "put_down_card_face_up", "verify_idle"],
        }

    if name == "put_down_card":
        position = action.get("position", "left")
        face_up = bool(action.get("face_up", False))
        instr = INSTR_PUT_DOWN.get((position, face_up))
        if instr is None:
            raise ValueError(f"invalid put_down_card position={position} face_up={face_up}")
        return {
            "prefix": "reset",
            "commands": [_cmd(instr)],
            "command_steps": ["put_down_card"],
            "sequence_steps": ["put_down_card", "verify_idle"],
        }

    if name in ("check", "fold"):
        return {"prefix": None, "commands": [], "command_steps": [], "sequence_steps": [name]}

    if name == "call":
        amount, computed = compute_call_amount(action, table)
        if amount <= 0:
            return {
                "prefix": None,
                "commands": [],
                "command_steps": [],
                "sequence_steps": [name],
                "computed": {**computed, "physical_bet_chips": amount},
            }
        inventory = resolve_chip_inventory(action, chips, table)
        if inventory is None:
            raise ValueError("call requires my_chips inventory")
        counts = split_chips_exact(amount, inventory)
        commands, command_steps = chip_commands_and_steps(counts)
        return {
            "prefix": "reset",
            "commands": commands,
            "command_steps": command_steps,
            "sequence_steps": command_steps + ["verify_idle"],
            "chip_counts": {str(value): count for value, count in sorted(counts.items())},
            "computed": {**computed, "physical_bet_chips": amount},
        }

    if name == "raise":
        amount, computed = compute_raise_amount(action, table)
        if amount <= 0:
            return {
                "prefix": None,
                "commands": [],
                "command_steps": [],
                "sequence_steps": [name],
                "computed": {**computed, "physical_bet_chips": amount},
            }
        inventory = resolve_chip_inventory(action, chips, table)
        if inventory is None:
            raise ValueError("raise requires my_chips inventory")
        counts = split_chips_exact(amount, inventory)
        commands, command_steps = chip_commands_and_steps(counts)
        return {
            "prefix": "reset",
            "commands": commands,
            "command_steps": command_steps,
            "sequence_steps": command_steps + ["verify_idle"],
            "chip_counts": {str(value): count for value, count in sorted(counts.items())},
            "computed": {**computed, "physical_bet_chips": amount},
        }

    if name == "all_in":
        inventory = resolve_chip_inventory(action, chips, table)
        counts = normalize_chip_map(inventory)
        if not counts:
            raise ValueError("all_in requires chip inventory")
        commands, command_steps = chip_commands_and_steps(counts)
        return {
            "prefix": "reset",
            "commands": commands,
            "command_steps": command_steps,
            "sequence_steps": command_steps + ["verify_idle"],
            "chip_counts": {str(value): count for value, count in sorted(counts.items())},
        }

    if name in ("collect_winnings", "pull_back_chips"):
        sources, computed = compute_collect_sources(action, table)
        counts = add_chip_maps(*(source["chip_counts"] for source in sources))
        if not counts:
            return {
                "prefix": None,
                "commands": [],
                "command_steps": [],
                "sequence_steps": [name],
                "chip_counts": {},
                "computed": {**computed, "physical_collect_chips": 0},
                "source_zones": sources,
            }
        commands = []
        command_steps = []
        source_zones = []
        for source in sources:
            source_counts = {value: count for value, count in source["chip_counts"].items() if count > 0}
            if not source_counts:
                continue
            source_commands, source_steps = chip_commands_and_steps(source_counts, INSTR_PULL, f"pull_{source['source']}")
            commands.extend(source_commands)
            command_steps.extend(source_steps)
            source_zones.append(
                {
                    "source": source["source"],
                    "chip_counts": {str(value): count for value, count in sorted(source_counts.items())},
                    "steps": source_steps,
                }
            )
        return {
            "prefix": "reset",
            "commands": commands,
            "command_steps": command_steps,
            "sequence_steps": command_steps + ["verify_idle"],
            "chip_counts": {str(value): count for value, count in sorted(counts.items())},
            "source_zones": source_zones,
            "computed": computed,
        }

    raise ValueError(f"unknown action {name!r}")


def main():
    parser = argparse.ArgumentParser(description="Translate action JSON to robot commands.")
    parser.add_argument("--action", required=True)
    parser.add_argument("--chips")
    parser.add_argument("--table")
    parser.add_argument("--as-sequence-cache", action="store_true")
    parser.add_argument("--sequence-id")
    parser.add_argument("--loop-stage", default="acting", choices=sorted(STAGES))
    args = parser.parse_args()

    try:
        action = json.loads(args.action)
        chips = json.loads(args.chips) if args.chips else None
        table = json.loads(args.table) if args.table else None
        translation = translate(action, chips=chips, table=table)
        if args.as_sequence_cache:
            output = parse_translation_as_sequence_cache(
                action,
                translation,
                sequence_id=args.sequence_id,
                loop_stage=args.loop_stage,
            )
        else:
            output = translation
        print(json.dumps(output, indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
