#!/usr/bin/env python3
"""Deterministic column-level evaluator for perception benchmark runs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROBLEMS_DIR = ROOT / "bench" / "problems"
GROUND_TRUTH = PROBLEMS_DIR / "ground_truth.json"
PROBLEM_TYPES = PROBLEMS_DIR / "problem_types.json"

DENOMS = ("5", "10", "50", "100")
COLUMNS = (
    "overall",
    "stage",
    "community",
    "turn",
    "blind",
    "bet",
    "my_chips",
    "opp_chips",
    "outcome",
)


def parse_problem_names(text: str) -> list[str]:
    return [item.strip() for item in re.split(r"[\s,]+", text) if item.strip()]


def load_problem_filter(args: argparse.Namespace) -> set[str] | None:
    if args.problem_list and args.problem_list_file:
        raise SystemExit("use only one of --problem-list or --problem-list-file")
    if args.problem_list_file:
        return set(parse_problem_names(Path(args.problem_list_file).read_text()))
    if args.problem_list:
        return set(parse_problem_names(args.problem_list))
    return None


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def get_path(data: Any, path: str) -> Any:
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def first_value(data: dict[str, Any], paths: list[str]) -> Any:
    for path in paths:
        value = get_path(data, path)
        if value is not None:
            return value
    return None


def normalize_token(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    text = text.replace("-", "_").replace(" ", "_")
    text = re.sub(r"[^a-z0-9_]+", "", text)
    return text


def normalize_stage(value: Any) -> str | None:
    token = normalize_token(value)
    if token in {
        "idle",
        "acting",
        "atom_idle",
        "down",
        "to_recover",
        "win",
        "lose",
        "show_hand",
    }:
        return token
    return None


def normalize_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    token = normalize_token(value)
    if token in {"true", "yes", "my_turn", "robot", "robot_turn", "our_turn"}:
        return True
    if token in {"false", "no", "opponent", "opponent_turn", "not_my_turn"}:
        return False
    return None


def normalize_blind(value: Any) -> str | None:
    token = normalize_token(value)
    if not token:
        return None
    if token in {"big_blind", "bigblind", "bb"}:
        return "big_blind"
    if token in {"small_blind", "smallblind", "sb"}:
        return "small_blind"
    if token in {"none", "no_blind"}:
        return "none"
    if "big_blind" in token or "bigblind" in token:
        return "big_blind"
    if "small_blind" in token or "smallblind" in token:
        return "small_blind"
    return None


def infer_robot_blind(summary: dict[str, Any]) -> str | None:
    direct = first_value(summary, ["blind", "table.blind", "robot_blind"])
    normalized = normalize_blind(direct)
    if normalized:
        return normalized

    for prefix in ("blind_assignment", "blinds", "blind_buttons", "buttons"):
        obj = summary.get(prefix)
        if not isinstance(obj, dict):
            continue
        big = normalize_token(obj.get("big_blind"))
        small = normalize_token(obj.get("small_blind"))
        if big and any(word in big for word in ("robot", "player", "my", "near", "lower")):
            return "big_blind"
        if small and any(word in small for word in ("robot", "player", "my", "near", "lower")):
            return "small_blind"
    return None


def normalize_card(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        for key in ("card", "read", "value", "name"):
            card = normalize_card(value.get(key))
            if card:
                return card
        return None
    text = str(value).strip()
    if not text or text.lower() in {"null", "none", "unknown", "unreadable", "face_down"}:
        return None
    text = text.replace("10", "T")
    match = re.search(r"([2-9TJQKA])\s*([cdhsCDHS])", text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).upper() + match.group(2).lower()


def normalize_cards(value: Any) -> list[str] | None:
    if isinstance(value, dict):
        for key in ("cards", "cards_left_to_right", "community_cards", "values"):
            cards = normalize_cards(value.get(key))
            if cards is not None:
                return cards
        return None
    if not isinstance(value, list):
        return None
    cards = [normalize_card(item) for item in value]
    return [card for card in cards if card is not None]


def chip_dict(value: Any) -> dict[str, int | None] | None:
    if not isinstance(value, dict):
        return None
    aliases = {
        "5": ("5", "red_5", "red", "five"),
        "10": ("10", "blue_10", "blue", "ten"),
        "50": ("50", "green_50", "green", "fifty"),
        "100": ("100", "brown_100", "brown", "hundred"),
    }
    out: dict[str, int | None] = {}
    for denom, keys in aliases.items():
        for key in keys:
            if key in value:
                raw = value[key]
                if raw is None:
                    out[denom] = None
                elif isinstance(raw, bool):
                    out[denom] = None
                elif isinstance(raw, (int, float)) and int(raw) == raw:
                    out[denom] = int(raw)
                else:
                    try:
                        out[denom] = int(str(raw).strip())
                    except ValueError:
                        out[denom] = None
                break
    return out if out else None


def first_chip_dict(summary: dict[str, Any], paths: list[str]) -> dict[str, int | None] | None:
    for path in paths:
        value = chip_dict(get_path(summary, path))
        if value is not None:
            return value
    return None


def normalize_outcome(value: Any) -> str | None:
    token = normalize_token(value)
    if not token:
        return None
    if token in {"win", "won", "collect_winnings", "robot_win", "my_win"}:
        return "win"
    if token in {"lose", "loss", "lost", "hand_lost", "robot_lose", "my_loss"}:
        return "lose"
    if token in {"tie", "draw", "chop"}:
        return "tie"
    if "not_showdown" in token:
        return None
    if "win" in token and "not" not in token:
        return "win"
    if "lose" in token or "loss" in token or "lost" in token:
        return "lose"
    return None


def extract_prediction(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "stage": normalize_stage(
            first_value(summary, ["loop_stage", "overall.loop_stage", "state.loop_stage"])
        ),
        "turn": normalize_bool(
            first_value(
                summary,
                [
                    "is_my_turn",
                    "table.is_my_turn",
                    "turn_detection.is_my_turn",
                    "turn.is_my_turn",
                    "findings.is_my_turn",
                    "findings.your_turn_marker_visible",
                ],
            )
        ),
        "blind": infer_robot_blind(summary),
        "community": normalize_cards(
            first_value(
                summary,
                [
                    "community_cards",
                    "table.community_cards",
                    "community_cards.cards",
                    "community_cards.cards_left_to_right",
                ],
            )
        ),
        "my_chips": first_chip_dict(
            summary,
            [
                "my_chips",
                "table.my_chips",
                "chip_inventory.my_chips",
                "chip_inventory.robot",
                "inventory.robot",
                "inventory_chips.robot",
                "chips.robot",
            ],
        ),
        "opp_chips": first_chip_dict(
            summary,
            [
                "opponent_chips",
                "table.opponent_chips",
                "chip_inventory.opponent_chips",
                "chip_inventory.opponent",
                "inventory.opponent",
                "inventory_chips.opponent",
                "chips.opponent",
            ],
        ),
        "my_bet": first_chip_dict(
            summary,
            [
                "my_current_bet",
                "table.my_current_bet",
                "bets.my_current_bet",
                "bets.player_side",
                "current_bets.robot",
            ],
        ),
        "opp_bet": first_chip_dict(
            summary,
            [
                "opponent_bet",
                "table.opponent_bet",
                "bets.opponent_bet",
                "bets.opponent_current_bet",
                "bets.opponent_side",
                "current_bets.opponent",
            ],
        ),
        "outcome": normalize_outcome(
            first_value(
                summary,
                [
                    "showdown_outcome",
                    "showdown.outcome",
                    "winner",
                    "outcome",
                    "loop_stage",
                    "decision.expected_route",
                    "expected_route",
                ],
            )
        ),
    }


def exact_chips(pred: dict[str, int | None] | None, truth: dict[str, Any]) -> bool:
    if pred is None:
        return False
    return all(pred.get(denom) == int(truth.get(denom, -9999)) for denom in DENOMS)


def exact_bets(pred_my: dict[str, int | None] | None, pred_opp: dict[str, int | None] | None, truth: dict[str, Any]) -> bool:
    table = truth["label"]["table"]
    return exact_chips(pred_my, table["my_current_bet"]) and exact_chips(pred_opp, table["opponent_bet"])


def truth_outcome(truth: dict[str, Any]) -> str | None:
    label = truth["label"]
    stage = normalize_stage(label.get("loop_stage"))
    if stage in {"win", "lose"}:
        return stage
    route = normalize_outcome(truth.get("expected_route"))
    if route:
        return route
    return None


def load_reference_data() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    ground_truth = {r["problem_id"]: r for r in load_json(GROUND_TRUTH)}
    problem_types = {r["problem_id"]: r for r in load_json(PROBLEM_TYPES)["problems"]}
    return ground_truth, problem_types


def problem_sort_key(problem_id: str) -> int | str:
    if problem_id.startswith("p") and problem_id[1:].isdigit():
        return int(problem_id[1:])
    return problem_id


def load_batch(batch_dir: Path) -> dict[str, Any]:
    for name in ("manifest.json", "summary.json"):
        path = batch_dir / name
        if path.exists():
            return load_json(path)
    raise FileNotFoundError(f"no manifest.json or summary.json in {batch_dir}")


def run_id_for_problem(batch: dict[str, Any], problem_id: str) -> str:
    variant = batch.get("visual_variant") or f"{batch['harness']}_native"
    return f"{problem_id}_{variant}_{batch['visual_setting']}_{batch['run_prefix']}"


def denominator_ids(column: str, problem_types: dict[str, dict[str, Any]], ground_truth: dict[str, dict[str, Any]], community_scope: str) -> list[str]:
    ids = sorted(problem_types, key=lambda p: int(p[1:]))
    if column in {"overall", "stage", "turn", "blind"}:
        return ids
    if column == "outcome":
        return [p for p in ids if problem_types[p]["coarse_type"] == "outcome_judge"]
    if column in {"bet", "my_chips", "opp_chips"}:
        return [
            p
            for p in ids
            if problem_types[p]["coarse_type"] in {"table_decision", "outcome_judge"}
        ]
    if column == "community":
        if community_scope == "visible":
            return [
                p
                for p in ids
                if len(ground_truth[p]["label"]["table"].get("community_cards") or []) > 0
            ]
        return [
            p
            for p in ids
            if problem_types[p]["coarse_type"] in {"table_decision", "outcome_judge"}
            and len(ground_truth[p]["label"]["table"].get("community_cards") or []) > 0
        ]
    raise ValueError(f"unknown column: {column}")


def relevant_columns(problem_type: dict[str, Any], truth: dict[str, Any]) -> list[str]:
    coarse = problem_type["coarse_type"]
    cols = ["stage", "turn", "blind"]
    if coarse in {"table_decision", "outcome_judge"}:
        cols.extend(["bet", "my_chips", "opp_chips"])
        if truth["label"]["table"].get("community_cards"):
            cols.append("community")
    if coarse == "outcome_judge":
        cols.append("outcome")
    if problem_type["primary_type"] == "held_card_read":
        # Held-card scoring is not a table column yet; keep overall aligned to
        # visible paper-table columns.
        pass
    return list(dict.fromkeys(cols))


def score_column(column: str, pred: dict[str, Any], truth: dict[str, Any]) -> tuple[bool, str]:
    label = truth["label"]
    table = label["table"]
    if column == "stage":
        expected = normalize_stage(label.get("loop_stage"))
        return pred["stage"] == expected, f"pred={pred['stage']} expected={expected}"
    if column == "turn":
        expected = bool(table["is_my_turn"])
        return pred["turn"] == expected, f"pred={pred['turn']} expected={expected}"
    if column == "blind":
        expected = normalize_blind(label.get("blind"))
        return pred["blind"] == expected, f"pred={pred['blind']} expected={expected}"
    if column == "community":
        expected = [normalize_card(card) for card in table.get("community_cards", [])]
        if pred["community"] == expected:
            return True, f"pred={pred['community']} expected={expected} match=ordered"
        if pred["community"] == list(reversed(expected)):
            return True, f"pred={pred['community']} expected={expected} match=reversed"
        return False, f"pred={pred['community']} expected={expected}"
    if column == "bet":
        ok = exact_bets(pred["my_bet"], pred["opp_bet"], truth)
        return ok, f"pred_my={pred['my_bet']} pred_opp={pred['opp_bet']}"
    if column == "my_chips":
        ok = exact_chips(pred["my_chips"], table["my_chips"])
        return ok, f"pred={pred['my_chips']} expected={table['my_chips']}"
    if column == "opp_chips":
        ok = exact_chips(pred["opp_chips"], table["opponent_chips"])
        return ok, f"pred={pred['opp_chips']} expected={table['opponent_chips']}"
    if column == "outcome":
        expected = truth_outcome(truth)
        return pred["outcome"] == expected, f"pred={pred['outcome']} expected={expected}"
    raise ValueError(f"unsupported scalar column: {column}")


def run_output_status(run_dir: Path, summary_name: str) -> tuple[bool, str, Path]:
    output_check = run_dir / "output_check.json"
    summary_path = run_dir / summary_name
    detail = ""
    valid = False
    if output_check.exists():
        try:
            valid = bool(load_json(output_check).get("ok"))
        except Exception as exc:  # noqa: BLE001
            detail = f"bad output_check: {exc}"
    if not valid:
        return False, detail or "missing_or_invalid_output_check", summary_path
    if not summary_path.exists():
        return False, f"missing_{summary_name}", summary_path
    return True, "", summary_path


def score_run_columns(
    *,
    problem_id: str,
    run_id: str,
    run_dir: Path,
    columns: list[str],
    summary_name: str,
    problem_types: dict[str, dict[str, Any]],
    ground_truth: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    valid, invalid_detail, summary_path = run_output_status(run_dir, summary_name)
    rows = []
    pred = None
    if valid:
        try:
            pred = extract_prediction(load_json(summary_path))
        except Exception as exc:  # noqa: BLE001
            valid = False
            invalid_detail = f"evaluation_error: {exc}"

    for column in columns:
        if not valid or pred is None:
            ok = False
            detail = invalid_detail
        elif column == "overall":
            subcols = relevant_columns(problem_types[problem_id], ground_truth[problem_id])
            subresults = [score_column(sub, pred, ground_truth[problem_id]) for sub in subcols]
            ok = all(item[0] for item in subresults)
            detail = "; ".join(f"{sub}:{item[1]}" for sub, item in zip(subcols, subresults))
        else:
            try:
                ok, detail = score_column(column, pred, ground_truth[problem_id])
            except Exception as exc:  # noqa: BLE001
                ok = False
                detail = f"evaluation_error: {exc}"
        rows.append(
            {
                "problem_id": problem_id,
                "run_id": run_id,
                "run_dir": str(run_dir),
                "ok": ok,
                "detail": detail,
            }
        )
    return rows


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    batch_dir = Path(args.batch_dir).resolve()
    batch = load_batch(batch_dir)
    ground_truth, problem_types = load_reference_data()
    problem_filter = load_problem_filter(args)
    if problem_filter:
        unknown = sorted(problem_filter - set(problem_types), key=problem_sort_key)
        if unknown:
            raise SystemExit(f"unknown problem ids in filter: {', '.join(unknown)}")

    columns = list(COLUMNS) if args.column == "all" else [args.column]
    results = []
    summaries: dict[str, Any] = {}
    for column in columns:
        problem_ids = denominator_ids(column, problem_types, ground_truth, args.community_scope)
        if problem_filter:
            problem_ids = [p for p in problem_ids if p in problem_filter]
        column_rows = []
        for problem_id in problem_ids:
            run_id = run_id_for_problem(batch, problem_id)
            run_dir = PROBLEMS_DIR / problem_id / "runs" / run_id
            column_rows.extend(
                score_run_columns(
                    problem_id=problem_id,
                    run_id=run_id,
                    run_dir=run_dir,
                    columns=[column],
                    summary_name=args.summary_name,
                    problem_types=problem_types,
                    ground_truth=ground_truth,
                )
            )
        correct = sum(int(row["ok"]) for row in column_rows)
        summaries[column] = {
            "correct": correct,
            "total": len(problem_ids),
            "accuracy": round(correct / len(problem_ids), 6) if problem_ids else None,
        }
        results.extend({"column": column, **row} for row in column_rows)

    report = {
        "batch_dir": str(batch_dir),
        "visual_variant": batch.get("visual_variant"),
        "visual_setting": batch.get("visual_setting"),
        "run_prefix": batch.get("run_prefix"),
        "community_scope": args.community_scope,
        "problem_filter": sorted(problem_filter, key=lambda p: int(p[1:])) if problem_filter else None,
        "summaries": summaries,
        "results": results,
    }
    return report


def evaluate_single_run(args: argparse.Namespace) -> dict[str, Any]:
    ground_truth, problem_types = load_reference_data()
    problem_id = args.problem_id
    if not problem_id:
        raise SystemExit("--problem-id is required with --run-id or --run-dir")
    if problem_id not in problem_types:
        raise SystemExit(f"unknown problem id: {problem_id}")
    if args.run_id and args.run_dir:
        raise SystemExit("use only one of --run-id or --run-dir")
    if not args.run_id and not args.run_dir:
        raise SystemExit("single-run mode requires --run-id or --run-dir")

    if args.run_dir:
        run_dir = Path(args.run_dir).resolve()
        run_id = run_dir.name
    else:
        run_id = args.run_id
        run_dir = PROBLEMS_DIR / problem_id / "runs" / run_id

    if args.column == "all":
        columns = ["overall", *relevant_columns(problem_types[problem_id], ground_truth[problem_id])]
    else:
        columns = [args.column]

    rows = score_run_columns(
        problem_id=problem_id,
        run_id=run_id,
        run_dir=run_dir,
        columns=columns,
        summary_name=args.summary_name,
        problem_types=problem_types,
        ground_truth=ground_truth,
    )
    summaries = {
        column: {
            "correct": int(row["ok"]),
            "total": 1,
            "accuracy": 1.0 if row["ok"] else 0.0,
        }
        for column, row in zip(columns, rows)
    }
    return {
        "mode": "single_run",
        "problem_id": problem_id,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "summary_name": args.summary_name,
        "community_scope": args.community_scope,
        "summaries": summaries,
        "results": [{"column": column, **row} for column, row in zip(columns, rows)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-dir", help="perception_eval/batch_runs/<batch-id>")
    parser.add_argument("--problem-id", help="Problem id for single-run mode, e.g. p3")
    parser.add_argument("--run-id", help="Run folder name under bench/problems/<problem-id>/runs/")
    parser.add_argument("--run-dir", help="Explicit run directory for single-run mode")
    parser.add_argument("--column", choices=("all",) + COLUMNS, required=True)
    parser.add_argument(
        "--community-scope",
        choices=("high", "visible"),
        default="high",
        help="community denominator: high-priority visible board states (13) or every visible board state (36)",
    )
    parser.add_argument("--out-json", help="optional path for detailed JSON output")
    parser.add_argument("--out-csv", help="optional path for per-problem CSV output")
    parser.add_argument("--problem-list", help="Comma-separated problem ids to score, e.g. p1,p3,p8")
    parser.add_argument("--problem-list-file", help="File containing problem ids separated by commas or whitespace")
    parser.add_argument(
        "--summary-name",
        default="visual_summary.json",
        help="run summary filename to evaluate, e.g. normalized_visual_summary.json",
    )
    args = parser.parse_args()

    direct_mode = bool(args.run_id or args.run_dir or args.problem_id)
    if args.batch_dir and direct_mode:
        raise SystemExit("use --batch-dir or single-run options, not both")
    if not args.batch_dir and not direct_mode:
        raise SystemExit("provide --batch-dir, or provide --problem-id with --run-id/--run-dir")

    report = evaluate_single_run(args) if direct_mode else evaluate(args)
    if args.out_json:
        Path(args.out_json).write_text(json.dumps(report, indent=2) + "\n")
    if args.out_csv:
        with Path(args.out_csv).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["column", "problem_id", "run_id", "run_dir", "ok", "detail"])
            writer.writeheader()
            for row in report["results"]:
                writer.writerow({key: row.get(key, "") for key in writer.fieldnames})

    for column, summary in report["summaries"].items():
        accuracy = summary["accuracy"]
        accuracy_text = "n/a" if accuracy is None else f"{accuracy:.3f}"
        print(
            f"{column}: {summary['correct']}/{summary['total']} "
            f"({accuracy_text})"
        )


if __name__ == "__main__":
    main()
