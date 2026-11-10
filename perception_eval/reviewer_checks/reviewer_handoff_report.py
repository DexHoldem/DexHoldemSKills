"""Build paper-column tables and annotated-history stability comparisons."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from audit_original import audit
from history_ablation import load_module

CONFIGS = [
    ("Codex", "GPT 6 Astra", "gpt-6-astra"),
    ("Codex", "GPT 6 Sol", "gpt-6-sol"),
    ("Codex", "GPT 5.6 Sol", "gpt-5.6-sol"),
    ("Codex", "GPT 5.6 Luna", "gpt-5.6-luna"),
    ("Codex", "GPT 5.5", None), ("Codex", "GPT 5.4", None),
    ("Codex", "GPT 5.4 mini", None),
    ("Claude Code", "Opus 5.5", "claude-opus-5-5"),
    ("Claude Code", "Sonnet 5", "claude-sonnet-5"),
    ("Claude Code", "Opus 4.7", "claude-opus-4-7"),
    ("Claude Code", "Sonnet 4.6", "claude-sonnet-4-6"),
    ("Claude Code", "Haiku 4.5", "claude-haiku-4-5"),
    ("Gemini CLI", "Gemini 3 Flash", "gemini-3-flash-preview"),
    ("Gemini CLI", "Gemini 3.1 Flash L.", "gemini-3.1-flash-lite-preview"),
]
COLUMNS = ["overall", "stage", "turn", "blind", "community", "bet", "my_chips", "opp_chips", "outcome"]
HEADERS = ["Harness", "Perceiver", "Overall", "LS", "TO", "BI", "CC", "CB", "RCI", "OCI", "SO", "Avg"]


def audit_fields(repo: Path, results: Path) -> dict[str, int]:
    """Recompute every applicable paper field from portable model outputs.

    Args:
        repo (Path): Checkout containing the unchanged scorer and gold labels.
        results (Path): Native score export with records and source outputs.

    Returns:
        dict[str, int]: Number of verified trials and applicable field scores.
    """
    ec = load_module(repo / "perception_eval/evaluate_column.py", "handoff_field_audit")
    truth, types = ec.load_reference_data()
    denominators = {c: set(ec.denominator_ids(c, types, truth, "high")) for c in COLUMNS}
    records = [json.loads(s) for s in (results / "records.jsonl").read_text().splitlines()]
    sources = [json.loads(s) for s in (results / "source_outputs.jsonl").read_text().splitlines()]
    indexed = {(r["model"], r["repeat"], r["problem"]): r for r in records}
    if len(indexed) != len(records) or len(sources) != len(records):
        raise ValueError("Duplicate or missing native scoring evidence")
    count = 0
    seen = set()
    for source in sources:
        key = (source["model"], source["repeat"], source["problem"])
        if key in seen:
            raise ValueError("Duplicate source output")
        seen.add(key)
        record, pid = indexed[key], source["problem"]
        valid = json.loads(source["output_check_text"] or "{}").get("ok")
        prediction = ec.extract_prediction(json.loads(source["visual_summary_text"])) if valid else None
        expected = {}
        for column, problems in denominators.items():
            if pid not in problems:
                continue
            applicable = ec.relevant_columns(types[pid], truth[pid]) if column == "overall" else [column]
            expected[column] = prediction is not None and all(ec.score_column(c, prediction, truth[pid])[0] for c in applicable)
        if expected != record["field_scores"]:
            raise ValueError(f"Native paper field mismatch: {key}")
        count += len(expected)
    summary = json.loads((results / "summary.json").read_text())
    for model in summary["models"]:
        selected = [r for r in records if r["model"] == model["model"]]
        for column in COLUMNS:
            values = [r["field_scores"][column] for r in selected if column in r["field_scores"]]
            expected = {"correct": sum(values), "total": len(values), "accuracy": sum(values) / len(values)}
            if expected != model["fields"][column]:
                raise ValueError("Native aggregate field mismatch")
        average = sum(model["fields"][c]["accuracy"] for c in COLUMNS[1:]) / 8
        if abs(average - model["field_average"]) > 1e-12:
            raise ValueError("Native field average mismatch")
    return {"trials": len(records), "applicable_field_scores": count}


def paper_rows(tex: Path) -> dict[str, list[float]]:
    """Read the fourteen published table rows from the supplied LaTeX source.

    Args:
        tex (Path): Paper experiments section with the perception table.

    Returns:
        dict[str, list[float]]: Display name mapped to ten paper percentages.
    """
    rows = {}
    for line in tex.read_text().splitlines():
        parts = line.split("&")
        if len(parts) != 12:
            continue
        name = parts[1].strip()
        if name not in {name for _, name, _ in CONFIGS}:
            continue
        values = [re.findall(r"\d+\.\d+", part) for part in parts[2:]]
        if any(len(value) != 1 for value in values):
            raise ValueError("Unexpected published table cell")
        rows[name] = [float(value[0]) for value in values]
    if len(rows) != 14:
        raise ValueError("Expected all fourteen original paper configurations")
    return rows


def build(repo: Path, paper: Path, native: Path, annotated: Path, output: Path, allow_incomplete: bool) -> dict:
    """Create source-traceable tables without imputing unavailable experiments.

    Args:
        repo (Path): DexHoldem checkout containing original stability archive.
        paper (Path): Exact experiments.tex used for the published control.
        native (Path): Newly scored original-script ablation directory.
        annotated (Path): New annotated GPT supplement, distinct from old runs.
        output (Path): Destination for handoff Markdown and machine data.
        allow_incomplete (bool): Permit an explicitly marked internal preview.

    Returns:
        dict: Combined source data and independent verification counts.
    """
    original = repo / "perception_eval/reviewer_checks/results/2026-11-10_original_stability"
    original_audit = audit(repo, original)
    native_audit = audit(repo, native)
    field_audit = audit_fields(repo, native)
    annotated_audit = audit(repo, annotated)
    annotated_field_audit = audit_fields(repo, annotated)
    annotated_report = json.loads((annotated / "summary.json").read_text())
    if not annotated_report.get("retains_annotated_history"):
        raise ValueError("Annotated supplement has the wrong input condition")
    if (annotated_report["pending"] or len(annotated_report["models"]) != 4) and not allow_incomplete:
        raise ValueError("Cannot publish before all four annotated GPT supplements complete")
    new_report = json.loads((native / "summary.json").read_text())
    if (new_report["pending"] or len(new_report["models"]) != 11) and not allow_incomplete:
        raise ValueError("Cannot publish while any accessible configuration is incomplete")
    old_report = json.loads((original / "summary.json").read_text())
    new = {row["model"]: row for row in new_report["models"]}
    fresh = {row["model"]: row for row in annotated_report["models"]}
    old = {row["model"]: row for row in old_report["models"]}
    published = paper_rows(paper)
    ec = load_module(repo / "perception_eval/evaluate_column.py", "handoff_original_scorer")
    truth, types = ec.load_reference_data()
    source_rows = [json.loads(s) for s in (original / "source_outputs.jsonl").read_text().splitlines()]
    reproduced = {}
    for _, name, _ in CONFIGS:
        selected = [row for row in source_rows if row["model"] == name]
        if not selected:
            continue
        column_results = {}
        for column in COLUMNS:
            problems = set(ec.denominator_ids(column, types, truth, "high"))
            scores = []
            for source in selected:
                pid = source["problem"]
                if pid not in problems:
                    continue
                valid = json.loads(source["output_check_text"] or "{}").get("ok")
                prediction = ec.extract_prediction(json.loads(source["visual_summary_text"])) if valid else None
                applicable = ec.relevant_columns(types[pid], truth[pid]) if column == "overall" else [column]
                scores.append(prediction is not None and all(ec.score_column(c, prediction, truth[pid])[0] for c in applicable))
            column_results[column] = 100 * sum(scores) / len(scores)
        values = [column_results[c] for c in COLUMNS]
        values += [sum(values[1:]) / 8]
        if any(abs(actual - reported) > 0.051 for actual, reported in zip(values, published[name])):
            raise ValueError(f"Original archive does not reproduce published row: {name}")
        reproduced[name] = values
    lines = ["# DexHoldem perception reviewer supplement", "",
        "Status: " + ("INTERNAL PREVIEW — incomplete models remain." if new_report["pending"] or annotated_report["pending"] else "All 11 accessible configurations complete: 1,188 native ablation trials, plus 432 new annotated GPT trials for missing scene-stability evidence. Each configuration/condition uses 36 scenes × 3 runs."), "",
        "## What changed", "",
        "**Without annotated history / cached information:** keep the original native paper script, prompt, guidelines, image-reading tools, output schema, validity check and deterministic scorer. Remove only historical parsed-state annotations, annotated action notes, action_sequence.json and hole_card_cache.json. Retain every historical/current image and s_current link. This is not current-image-only evaluation and is not autonomous history prediction.", "",
        "**With annotated history:** score the existing scene_stable predictions retrospectively for the ten configurations with retained paper logs. For GPT 6 Astra/6 Sol/5.6 Sol/5.6 Luna, whose old scene-level logs are unavailable, run 36 × 3 new annotated trials with the exact original paper script and original input bytes. These four fresh results are explicitly distinguished from historical runs and never substituted for the published paper table. The original Overall/field metrics below are copied from the exact paper table, and all ten configurations with available old raw outputs are independently reproduced.", "",
        "Each configuration averages three runs on the same 36 scenes. They are not 108 independent scenes. Column denominators per run are Overall/LS/TO/BI 36, CC 13, CB/RCI/OCI 16, SO 7. Avg equally weights the eight field accuracies and excludes Overall. Invalid model output remains wrong; no best-of or correctness-based reruns.", "",
        "## Original paper: with annotated history (%)", "",
        "| " + " | ".join(HEADERS) + " |", "|" + "---|" * len(HEADERS)]
    for harness, name, _ in CONFIGS:
        lines.append("| " + " | ".join([harness, name] + [f"{v:.1f}" for v in published[name]]) + " |")
    lines += ["", "## New annotated GPT supplement (%) — separate from the original paper", "",
              "These four fresh runs supply the missing WITH-history scene-stability predictions. Full original columns are retained for transparency; these are not the published historical results.", "",
              "| " + " | ".join(HEADERS) + " |", "|" + "---|" * len(HEADERS)]
    for harness, name, model in CONFIGS[:4]:
        row = fresh.get(model)
        values = [row["fields"][c]["accuracy"] * 100 for c in COLUMNS] + [row["field_average"] * 100] if row else None
        cells = [f"{v:.1f}" for v in values] if values else ["Pending"] * 10
        lines.append("| " + " | ".join([harness, name] + cells) + " |")
    lines += ["", "## New ablation: without annotated history / cached information (%)", "",
              "| " + " | ".join(HEADERS) + " |", "|" + "---|" * len(HEADERS)]
    no_history_table = []
    for harness, name, model in CONFIGS:
        row = new.get(model)
        values = [row["fields"][c]["accuracy"] * 100 for c in COLUMNS] + [row["field_average"] * 100] if row else None
        cells = [f"{v:.1f}" for v in values] if values else ["N/A" if model is None else "Pending"] * 10
        line = "| " + " | ".join([harness, name] + cells) + " |"
        lines.append(line)
        no_history_table.append(line)
    lines += ["", "N/A for GPT 5.5/5.4/5.4 mini means the retired model IDs were unavailable, not zero accuracy. No substitute model was used.", "",
              "## Scene-stability comparison (%)", "",
              "The score reads `table.scene_stable` directly, never infers stability from LS. Labels: 31 stable and 5 unstable scenes per run. Always-stable baseline: **86.1% accuracy, 100% stable recall, 0% unstable recall, 50% balanced accuracy**. Balanced accuracy averages the two class recalls. The original Overall definition remains unchanged.", "",
              "| Perceiver | History info | Accuracy | Stable recall | Unstable recall | Balanced accuracy | Missing/invalid /108 |", "|---|---|---:|---:|---:|---:|---:|"]
    paired = []
    for _, name, model in CONFIGS:
        with_history = old.get(name) or fresh.get(model)
        origin = "original paper" if name in old else "new supplement"
        pair = {"model": model or name, "name": name, "with_history": with_history, "with_history_source": origin, "without_history": new.get(model)}
        paired.append(pair)
        for setting, row in ((f"With ({origin})", with_history), ("Without", new.get(model))):
            if row:
                values = [row["accuracy"], row["stable"]["recall"], row["unstable"]["recall"], row["balanced_accuracy"]]
                cells = [f"{v*100:.1f}" for v in values] + [str(row["missing_or_invalid"])]
            else:
                cells = ["N/A"] * 5
            lines.append("| " + " | ".join([name, setting] + cells) + " |")
    lines += ["", "WITH-history GPT 6 Astra/6 Sol/5.6 Sol/5.6 Luna values are NEW original-script evaluations because their historical scene-level logs are unavailable. All other WITH-history values use original paper outputs. Their published aggregate scores cannot recover scene stability. The superseded tool-free experiment is excluded entirely. WITHOUT-history N/A for the three retired GPT IDs is an availability limit. Both settings are directly scored for all eleven accessible configurations; the source/time distinction is explicit.", "",
              "## Separate image-only held-card diagnostic", "",
              "This previously shared diagnostic contains 11 images × 3 runs × 11 configurations = 363 calls. It supplies only the current image and a neutral prompt, with no history or labels. It is a distinct rank-and-suit task, not a replacement for the original perception table.", "",
              "| Model | Correct /33 | Exact (%) | Card macro (%) | Balanced6 repeats /6 |", "|---|---:|---:|---:|---|"]
    held = []
    for family in ("claude", "gemini", "codex"):
        report = json.loads((repo / f"perception_eval/held_card/results/2026-11-09_{family}/summary.json").read_text())
        for row in report["models"]:
            repeats = row["repeats"]
            correct = sum(r["all11"]["correct"] for r in repeats)
            macro = sum(r["all11"]["macro_card_accuracy"] for r in repeats) / 3
            balanced = [r["balanced6"]["correct"] for r in repeats]
            lines.append(f"| {row['name']} | {correct} | {100*correct/33:.1f} | {100*macro:.1f} | {', '.join(map(str, balanced))} |")
            held.append({"model": row["model"], "correct": correct, "n": 33, "card_macro": macro, "balanced6": balanced})
    lines += ["", "Held-card labels remain proposed_visual_review; human verification is required. All 11 images show red suits, with only six card identities. Haiku's 0/33 reflects invalid output format and must not be described as zero visual ability. The preserved strict parser also rejects correct answers inside Markdown fences. No model ranking or general 52-card claim is supported by this small diagnostic.", "",
              "## Provenance and interpretation", "",
              "- Gemini 3 Flash: eight unanswered/unstarted quota trials were recovered using the unchanged original Gemini CLI with direct paid Google API authentication. All previous attempts are preserved; all eight returned the requested model ID. The original p29/repeat-3 answer remains despite its later CLI error because output_check passed. Invalid answers were not rerun.",
              "- Gemini 3.1 Flash Lite: the requested preview alias resolves to stable gemini-3.1-flash-lite in all 108 ablation records; it is not claimed identical to the historical preview snapshot.",
              "- Model service snapshots, CLI versions and billing routes may differ from the original runs. These comparisons are descriptive diagnostics, not an isolated causal estimate or a ranking under matched compute.",
              "- Scene-stability accuracy measures a predicted scene_stable field; it does not by itself measure downstream wait/continue/recover decisions or physical scene-preserving execution.",
              "- The problem-data ZIP separates the ablated input tree, the removed annotation/cache overlay, offline gold labels, and the held-card dataset. The logs/results ZIP contains raw outputs and attempts, portable scoring evidence, exact paper table source, and reproduction scripts. Never place offline labels or result logs in a model's input workspace.", ""]
    output.mkdir(parents=True, exist_ok=True)
    (output / "RESULTS.md").write_text("\n".join(lines))
    data = {"native": new_report, "original_stability": old_report, "published_original_fields": published,
            "original_fields_reproduced": reproduced, "stability_comparison": paired, "held_card": held,
            "original_audit": original_audit, "native_audit": native_audit,
            "native_field_audit": field_audit,
            "annotated_gpt_supplement": annotated_report, "annotated_audit": annotated_audit,
            "annotated_field_audit": annotated_field_audit,
            "paper_source_sha256": hashlib.sha256(paper.read_bytes()).hexdigest()}
    (output / "combined_results.json").write_text(json.dumps(data, indent=2) + "\n")
    (output / "paper_table_source.tex").write_text(paper.read_text())
    return data


def main() -> None:
    """Generate a final handoff only after every accessible model has finished."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "paper", "native", "annotated", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    result = build(args.repo, args.paper, args.native, args.annotated, args.output, args.allow_incomplete)
    print(json.dumps({"native_audit": result["native_audit"], "original_audit": result["original_audit"],
                      "original_paper_rows_reproduced": len(result["original_fields_reproduced"])}))


if __name__ == "__main__":
    main()
