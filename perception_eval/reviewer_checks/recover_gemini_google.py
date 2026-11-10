"""Recover unanswered quota failures using the unchanged runner and Google API."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import time
from pathlib import Path

from native_ablation import digest, dump, prepare, run_trial
from rolling_pool import rolling_map

MODEL = "gemini-3-flash-preview"
PROBLEMS = ("p26", "p27", "p28", "p32", "p33", "p34", "p35", "p36")
ROUTE = "google_gemini_developer_api_paid"


def eligible(root: Path, problem: str) -> bool:
    """Return whether a planned trial is unstarted or an unanswered quota error.

    Args:
        root (Path): Campaign directory with canonical records and raw runs.
        problem (str): Problem identifier in the frozen recovery plan.

    Returns:
        bool: True only when no answer exists and quota evidence is explicit.
            Any answered trial, including an invalid answer, is retained.
    """
    if problem not in PROBLEMS:
        raise ValueError("Problem is outside the frozen recovery plan")
    trial = root / "records" / MODEL / "repeat_3" / problem
    canonical = trial / "record.json"
    if not canonical.exists():
        if list(trial.glob("attempt_*")):
            raise ValueError("Unfinished attempt requires inspection before resuming")
        return True
    record = json.loads(canonical.read_text())
    folder = Path(record["run_dir"])
    if (folder / "visual_summary.json").exists():
        return False
    if record.get("recovery_route") == ROUTE:
        return False
    if record["status"] != "gemini_failed":
        return False
    evidence = "\n".join(p.read_text(errors="replace") for p in
                         (folder / "gemini_stdout.txt", folder / "gemini_stderr.txt") if p.is_file())
    return "429" in evidence and "RESOURCE_EXHAUSTED" in evidence


def recover(repo: Path, root: Path, problem: str) -> dict:
    """Run one prevalidated missing trial and preserve its preceding evidence.

    Args:
        repo (Path): Original benchmark source repository.
        root (Path): Existing ablated campaign directory.
        problem (str): Explicitly eligible recovery problem.

    Returns:
        dict: New original-runner record with authentication-route provenance.
    """
    if not eligible(root, problem):
        raise ValueError("Trial became ineligible; refusing to replace it")
    trial = root / "records" / MODEL / "repeat_3" / problem
    path = trial / "record.json"
    previous_sha = digest(path) if path.exists() else None
    if path.exists():
        backup = trial / "record_before_google_api.json"
        if backup.exists():
            raise ValueError("Recovery backup already exists")
        path.rename(backup)
    dump(trial / "google_recovery_started.json", {
        "started_unix": time.time(), "previous_record_sha256": previous_sha,
        "recovery_route": ROUTE, "prompt_or_tool_changes": False})
    record = run_trial(repo, root, MODEL, problem, 3)
    record.update(recovery_route=ROUTE, previous_record_sha256=previous_sha)
    dump(trial / f"attempt_{record['attempt']}" / "record.json", record)
    dump(path, record)
    return record


def main() -> None:
    """Run the frozen recovery plan under a provider lock and private API auth."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    repo, root, private = args.repo.resolve(), args.root.resolve(), args.private.resolve()
    with (root / "gemini.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        prepare(repo, root)
        plan = json.loads((root / "openrouter_recovery_plan.json").read_text())
        identities = {(r["model"], r["problem"], r["repeat"]) for r in plan["pending"]}
        if identities != {(MODEL, p, 3) for p in PROBLEMS}:
            raise ValueError("Recovery plan changed")
        smoke = json.loads((root / "google_api_smoke.json").read_text())
        if smoke["http_status"] != 200:
            raise ValueError("Google API connectivity was not verified")
        settings_path = private / "gemini_system_settings.json"
        default_system = Path("/Library/Application Support/GeminiCli/settings.json")
        settings = json.loads(default_system.read_text()) if default_system.exists() else {}
        settings.setdefault("security", {}).setdefault("auth", {})["selectedType"] = "gemini-api-key"
        dump(settings_path, settings)
        settings_path.chmod(0o600)
        os.environ["GEMINI_API_KEY"] = (private / "key").read_text().strip()
        os.environ["GEMINI_CLI_SYSTEM_SETTINGS_PATH"] = str(settings_path)
        for name in ("GOOGLE_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI", "GOOGLE_GEMINI_BASE_URL", "GOOGLE_VERTEX_BASE_URL"):
            os.environ.pop(name, None)
        jobs = [p for p in PROBLEMS if eligible(root, p)]
        retained = {str(p.relative_to(root)): digest(p) for p in
                    (root / "records").glob("gemini*/repeat_*/p*/record.json")
                    if not (p.parent.name in jobs and p.parent.parent.name == "repeat_3"
                            and p.parent.parent.parent.name == MODEL)}
        dump(root / "google_api_recovery_protocol.json", {
            "route": ROUTE, "model": MODEL, "repeat": 3, "planned": list(PROBLEMS),
            "pending_at_launch": jobs, "workers": args.workers, "started_unix": time.time(),
            "retained_record_sha256": retained, "source_manifest_sha256": digest(root / "protocol.json"),
            "inference_runner_changed": False, "prompt_changed": False, "tools_changed": False,
            "change": "Original Gemini CLI now authenticates directly with a paid Google API key; no proxy or fallback."})
        print("RECOVERY_START", jobs, flush=True)
        rows = rolling_map(jobs, lambda p: recover(repo, root, p), args.workers,
                           lambda r: r["status"] in {"gemini_failed", "wrapper_failed"})
        for name, expected in retained.items():
            if digest(root / name) != expected:
                raise ValueError(f"Retained record changed: {name}")
        report = {"finished_unix": time.time(), "returned": len(rows),
                  "rows": rows, "retained_records_verified": len(retained)}
        dump(root / "google_api_recovery_results.json", report)
        print("RECOVERY_FINISHED", len(rows), flush=True)


if __name__ == "__main__":
    main()
