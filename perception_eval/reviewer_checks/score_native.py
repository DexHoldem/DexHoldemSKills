"""Score completed native ablation configurations with the original paper rules."""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

from evaluate_stability import metrics, parse_stability
from history_ablation import load_module
from native_ablation import MODELS, digest, dump


def score(repo: Path, root: Path, output: Path) -> dict:
    """Export original fields and explicit stability for fully returned models.

    Args:
        repo (Path): Original source checkout containing scorer and gold labels.
        root (Path): Corrected native campaign directory.
        output (Path): Destination for portable records, sources and summaries.

    Returns:
        dict: Complete-model metrics, with pending configurations listed apart.
            Invalid model answers count wrong; unresolved transport trials do
            not produce a publishable model row. Three repeats share 36 scenes.
    """
    ec = load_module(repo / "perception_eval/evaluate_column.py", "native_paper_rules")
    protocol = json.loads((root / "protocol.json").read_text())
    annotated = protocol.get("retains_annotated_history", False)
    configurations = protocol.get("models", MODELS)
    truth, types = ec.load_reference_data()
    ids = sorted(truth, key=ec.problem_sort_key)
    if len(ids) != 36:
        raise ValueError("Expected the original 36 scenes")
    source_files = [repo / "perception_eval/evaluate_column.py", ec.GROUND_TRUTH, ec.PROBLEM_TYPES]
    denominator = {c: set(ec.denominator_ids(c, types, truth, "high")) for c in ec.COLUMNS}
    models, pending, records, sources = [], [], [], []
    for model, harness in configurations.items():
        paths = [root / "records" / model / f"repeat_{r}" / p / "record.json"
                 for r in range(1, 4) for p in ids]
        returned = [json.loads(p.read_text()) for p in paths if p.exists()]
        unresolved = [r for r in returned if r["status"] not in {"ok", "invalid_outputs"}
                      and not (r.get("wrapper_result") or {}).get("output_check", {}).get("ok")]
        if len(returned) != 108 or unresolved:
            pending.append({"model": model, "returned": len(returned), "planned": 108,
                            "unresolved_transport": len(unresolved),
                            "statuses": dict(Counter(r["status"] for r in returned))})
            continue
        selected, repeat_rows = [], []
        for row in returned:
            pid, run_dir = row["problem"], Path(row["run_dir"])
            valid, detail, summary_path = ec.run_output_status(run_dir, "visual_summary.json")
            summary_text = summary_path.read_text() if summary_path.exists() else None
            check_path = run_dir / "output_check.json"
            check_text = check_path.read_text() if check_path.exists() else None
            prediction, status = None, detail or "invalid_output"
            if valid:
                try:
                    prediction, status = parse_stability(json.loads(summary_text))
                except (ValueError, TypeError, AttributeError):
                    status = "invalid_summary"
            columns = [c for c in ec.COLUMNS if pid in denominator[c]]
            scores = ec.score_run_columns(problem_id=pid, run_id=row["run_id"], run_dir=run_dir,
                columns=columns, summary_name="visual_summary.json", problem_types=types, ground_truth=truth)
            field_scores = {c: s["ok"] for c, s in zip(columns, scores)}
            overall = field_scores["overall"]
            record = {"model": model, "harness": harness, "repeat": row["repeat"],
                "problem": pid, "run_id": row["run_id"], "truth": truth[pid]["label"]["table"]["scene_stable"],
                "prediction": prediction, "status": status, "runner_status": row["status"],
                "original_overall": overall, "field_scores": field_scores,
                "summary_sha256": digest(summary_path) if summary_path.exists() else None,
                "output_check_sha256": digest(check_path) if check_path.exists() else None,
                "recovery_route": row.get("recovery_route"),
                "source": str(summary_path.relative_to(root))}
            record["extended_overall"] = overall and prediction is record["truth"]
            selected.append(record)
            sources.append({k: record[k] for k in ("model", "repeat", "problem", "run_id", "summary_sha256", "output_check_sha256")}
                           | {"visual_summary_text": summary_text, "output_check_text": check_text})
        for repeat in range(1, 4):
            subset = [r for r in selected if r["repeat"] == repeat]
            repeat_rows.append({"repeat": repeat, **metrics(subset),
                                "original_overall": sum(r["original_overall"] for r in subset)})
        fields = {}
        for column in ec.COLUMNS:
            values = [r["field_scores"][column] for r in selected if column in r["field_scores"]]
            fields[column] = {"correct": sum(values), "total": len(values), "accuracy": sum(values) / len(values)}
        models.append({"model": model, "harness": harness, **metrics(selected), "fields": fields,
                       "original_overall": sum(r["original_overall"] for r in selected),
                       "extended_overall": sum(r["extended_overall"] for r in selected),
                       "field_average": sum(v["accuracy"] for c, v in fields.items() if c != "overall") / 8,
                       "paid_google_recovery_trials": sum(r["recovery_route"] is not None for r in selected),
                       "repeats": repeat_rows})
        records.extend(selected)
    output.mkdir(parents=True, exist_ok=True)
    description = ("New annotated GPT scene-stability supplement using the original paper scripts and all original historical annotations/caches. Does not replace published paper results."
                   if annotated else "Original native paper scripts; historical images retained; historical annotations and caches removed.")
    report = {"protocol": description, "retains_annotated_history": annotated,
              "created_unix": time.time(), "models": models, "pending": pending,
              "control": "Fresh annotated supplement, kept separate from published paper scores." if annotated else "Published original annotated-history runs; new GPT stability supplements reported separately.",
              "community_scope": "high", "independent_scenes": 36, "repeats": 3,
              "model_alias_note": "The requested gemini-3.1-flash-lite-preview alias reports gemini-3.1-flash-lite in all 108 CLI model-stat records; it is not claimed to be the historical preview snapshot."}
    dump(output / "summary.json", report)
    dump(output / "manifest.json", {"sources_sha256": {str(p.relative_to(repo)): digest(p) for p in source_files},
         "scorer_sha256": digest(Path(__file__)), "campaign_protocol_sha256": digest(root / "protocol.json")})
    for name, rows in (("records.jsonl", records), ("source_outputs.jsonl", sources)):
        (output / name).write_text("".join(json.dumps(r) + "\n" for r in rows))
    lines = ["# " + ("New annotated GPT supplement" if annotated else "Original-script perception ablation"), "",
        description + " Each complete row has three repeats of the same 36 scenes. Original paper scorer and validity gate are unchanged. Invalid model answers remain in the denominator.", "",
        "| Model | Overall /108 | LS | TO | BI | CC | CB | RCI | OCI | SO | Field avg | Stability | Unstable recall | Balanced acc. |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in models:
        fields = row["fields"]
        values = [fields[c]["accuracy"] for c in ("stage", "turn", "blind", "community", "bet", "my_chips", "opp_chips", "outcome")]
        values += [row["field_average"], row["accuracy"], row["unstable"]["recall"], row["balanced_accuracy"]]
        lines.append(f"| {row['model']} | {row['original_overall']} | " + " | ".join(f"{v*100:.1f}%" for v in values) + " |")
    lines += ["", "Scene stability is scored directly from scene_stable, never inferred from LS. Gold labels contain 31 stable and 5 unstable scenes; the always-stable baseline has 86.1% accuracy, 0% unstable recall, and 50% balanced accuracy.", "",
              "Gemini 3 Flash includes eight quota-recovery trials using the same CLI and native runner with direct paid Google API authentication. The remaining trials use the original CLI account route. This route change is disclosed; infrastructure is not claimed identical. The p29/repeat-3 answer is retained despite its later CLI error because its original output check passed.", "",
              "The requested Gemini 3.1 Flash Lite preview alias reports `gemini-3.1-flash-lite` in all 108 CLI model-stat records. This is not claimed to be the historical preview snapshot.", "",
              "Full native outputs and all attempts: [raw archive](raw_runs_and_attempts.tar.gz), with [per-file hashes](raw_archive_manifest.json). Portable scoring evidence: [source outputs](source_outputs.jsonl), [scene-level scores](records.jsonl), and [aggregate/per-repeat results](summary.json).", "",
              "Incomplete configurations are not ranked or presented as full results:" if pending else "All declared configurations are complete."]
    if annotated:
        lines = [line for line in lines if not line.startswith(("Gemini 3 Flash includes", "The requested Gemini 3.1"))]
        report.pop("model_alias_note")
        dump(output / "summary.json", report)
    lines += [f"- {r['model']}: {r['returned']}/108 returned; {r['unresolved_transport']} unresolved transport trials." for r in pending]
    (output / "README.md").write_text("\n".join(lines) + "\n")
    return report


def main() -> None:
    """Score and print compact completed-model counts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = score(args.repo.resolve(), args.root.resolve(), args.output.resolve())
    for row in report["models"]:
        print(row["model"], "Overall", row["original_overall"], "/108", "stability", row["correct"], "/108")
    print("Pending:", report["pending"])


if __name__ == "__main__":
    main()
