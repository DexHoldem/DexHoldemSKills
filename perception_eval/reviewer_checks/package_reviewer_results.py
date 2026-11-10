"""Package completed native results, original-control logs and held-card evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

SECRET = re.compile(rb"AIza[\w-]{30,}|sk-(?:or-v1-|ant-api\d+-|proj-)[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{15,}")


def package(repo: Path, campaign: Path, annotated: Path, held_card: Path, handoff: Path, output: Path) -> dict:
    """Export final evidence only when all eleven available models are complete.

    Args:
        repo (Path): Original source checkout and annotated-run logs.
        campaign (Path): Corrected ablation campaign with completed-model scores.
        annotated (Path): New annotated GPT supplement with all raw outputs.
        held_card (Path): Held-card dataset package with original CLI result logs.
        handoff (Path): Final combined report, paper source and data manifest.
        output (Path): Destination ZIP file.

    Returns:
        dict: Archive checksum and verified per-file source hashes.
    """
    summary = json.loads((campaign / "scored_completed/summary.json").read_text())
    if summary["pending"] or len(summary["models"]) != 11:
        raise ValueError("Final ZIP requires all eleven accessible configurations")
    annotated_summary = json.loads((annotated / "scored_completed/summary.json").read_text())
    if annotated_summary["pending"] or len(annotated_summary["models"]) != 4:
        raise ValueError("Final ZIP requires all four annotated GPT supplements")
    files: dict[str, Path] = {}

    def add_tree(source: Path, prefix: str, exclusions: set[str] | None = None) -> None:
        """Add regular source files (Path) under prefix (str), excluding names."""
        if not source.is_dir():
            raise ValueError(f"Missing required archive source: {source}")
        for path in source.rglob("*"):
            relative = path.relative_to(source)
            if not path.is_file() or any(p in (exclusions or set()) for p in relative.parts):
                continue
            if path.is_symlink():
                raise ValueError("Unexpected symlink in log archive")
            files[f"{prefix}/{relative.as_posix()}"] = path

    for name in ("RESULTS.md", "combined_results.json", "paper_table_source.tex"):
        files[name] = handoff / name
    files["problem_data_manifest.json"] = handoff.parent / "dexholdem_problem_data.manifest.json"
    add_tree(campaign / "scored_completed", "without_history/scores")
    add_tree(campaign / "records", "without_history/records", {"__pycache__"})
    run_dirs: set[Path] = set()
    for record in (campaign / "records").rglob("record.json"):
        row = json.loads(record.read_text())
        if row.get("run_dir"):
            run_dirs.add(Path(row["run_dir"]))
    for folder in run_dirs:
        relative = folder.relative_to(campaign)
        add_tree(folder, f"without_history/{relative.as_posix()}")
    add_tree(annotated / "scored_completed", "with_history_new_gpt/scores")
    add_tree(annotated / "records", "with_history_new_gpt/records", {"__pycache__"})
    annotated_runs = {Path(json.loads(path.read_text())["run_dir"])
                      for path in (annotated / "records").rglob("record.json")}
    for folder in annotated_runs:
        relative = folder.relative_to(annotated)
        add_tree(folder, f"with_history_new_gpt/{relative.as_posix()}")
    for name in ("protocol.json", "campaign_annotated_gpt.log", "codex_status.json"):
        files[f"with_history_new_gpt/{name}"] = annotated / name
    original = repo / "perception_eval/reviewer_checks/results/2026-11-10_original_stability"
    add_tree(original, "with_history/scores")
    original_runs = {Path(json.loads(s)["source"]).parent for s in (original / "records.jsonl").read_text().splitlines()}
    for relative in original_runs:
        folder = repo / relative
        add_tree(folder, f"with_history/raw/{relative.as_posix()}")
    add_tree(held_card / "results", "held_card/raw", {"__pycache__"})
    add_tree(repo / "perception_eval/held_card/results", "held_card/final_scores", {"__pycache__"})
    for path in (repo / "perception_eval/held_card").glob("*.py"):
        files[f"source/held_card/{path.name}"] = path
    files["source/held_card/README.md"] = repo / "perception_eval/held_card/README.md"
    for name in ("run_codex_benchmark.py", "run_claude_benchmark.py", "run_gemini_benchmark.py", "preflight.py", "default_prompt.py", "evaluate_column.py"):
        files[f"source/original_native/perception_eval/{name}"] = repo / "perception_eval" / name
    for name in ("ground_truth.json", "problem_types.json"):
        files[f"source/original_native/bench/problems/{name}"] = repo / "bench/problems" / name
    add_tree(repo / "skills/dexholdem-v2-native", "source/original_native/skills/dexholdem-v2-native", {"__pycache__"})
    add_tree(campaign / "paper_gpt_source", "source/exact_paper_gpt")
    helper_names = ("native_ablation.py", "rolling_pool.py", "resume_claude.py", "recover_gemini_google.py",
                    "score_native.py", "evaluate_stability.py", "audit_original.py", "history_ablation.py",
                    "providers.py", "export_native_snapshot.py",
                    "supplement_annotated_gpt.py", "test_supplement_annotated_gpt.py",
                    "package_reviewer_inputs.py", "reviewer_handoff_report.py", "package_reviewer_results.py")
    for name in helper_names:
        files[f"source/reviewer_helpers/{name}"] = Path(__file__).parent / name
    for name in ("protocol.json", "gpt_paper_provenance.json", "rolling_queue_transition.json", "claude_account_switch.json",
                 "google_api_recovery_protocol.json", "google_api_recovery_results.json", "gemini_quota_drain.json"):
        if (campaign / name).exists():
            files[f"protocol/{name}"] = campaign / name
    for path in campaign.glob("campaign_*.log"):
        files[f"controller_logs/{path.name}"] = path
    hashes = {}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(files.items()):
            data = path.read_bytes()
            if SECRET.search(data):
                raise ValueError(f"Credential-like content in {name}; refusing upload")
            hashes[name] = hashlib.sha256(data).hexdigest()
            archive.writestr(name, data)
        manifest = {"file_sha256": hashes, "native_configurations": 11, "native_trials": 1188,
                    "original_stability_configurations": 10, "original_stability_trials": 1080,
                    "new_annotated_gpt_configurations": 4, "new_annotated_gpt_trials": 432,
                    "held_card_configurations": 11, "held_card_trials": 363,
                    "native_run_directories_including_attempts": len(run_dirs),
                    "original_run_directories": len(original_runs), "credential_scan": "passed"}
        manifest["new_annotated_gpt_run_directories"] = len(annotated_runs)
        archive.writestr("ARCHIVE_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    with zipfile.ZipFile(output) as archive:
        for name, expected in hashes.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError("Results archive round-trip hash mismatch")
    manifest.update(zip_sha256=hashlib.sha256(output.read_bytes()).hexdigest(), zip_bytes=output.stat().st_size,
                    round_trip_verified=True)
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    """Build the completed result/log package for the authorized Slack channel."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "campaign", "annotated", "held-card", "handoff", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = package(args.repo, args.campaign, args.annotated, args.held_card, args.handoff, args.output)
    print(json.dumps({"files": len(result["file_sha256"]), "zip_bytes": result["zip_bytes"],
                      "sha256": result["zip_sha256"], "round_trip_verified": result["round_trip_verified"]}))


if __name__ == "__main__":
    main()
