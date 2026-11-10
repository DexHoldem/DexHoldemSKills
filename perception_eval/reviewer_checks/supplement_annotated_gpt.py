"""Supplement missing GPT scene-stability logs with the original annotated inputs."""
from __future__ import annotations

import argparse
import fcntl
import json
import shutil
import subprocess
import time
from pathlib import Path

from native_ablation import command, digest, dump
from rolling_pool import rolling_map

MODELS = ("gpt-6-astra", "gpt-6-sol", "gpt-5.6-sol", "gpt-5.6-luna")


def prepare(repo: Path, baseline: Path, root: Path) -> dict:
    """Copy precisely the original inputs, preserving all annotation/cache bytes.

    Args:
        repo (Path): Original dataset checkout, never modified.
        baseline (Path): Frozen no-annotation campaign holding source manifests.
        root (Path): Separate destination for this new annotated supplement.

    Returns:
        dict: Frozen inputs and exact archived GPT runner provenance.
    """
    base = json.loads((baseline / "protocol.json").read_text())
    provenance = json.loads((baseline / "gpt_paper_provenance.json").read_text())
    runner = baseline / "paper_gpt_source"
    for relative, expected in provenance["snapshot_sha256"].items():
        if digest(runner / relative) != expected:
            raise ValueError("Archived GPT source changed")
    inputs = {}
    for pid, specification in base["problems"].items():
        files = dict(specification["retained"])
        files.update({name: {"sha256": sha} for name, sha in specification["removed"].items()})
        inputs[pid] = files
    protocol = {"protocol": "supplemental_original_native_annotated_gpt_v1",
                "purpose": "New scene-stability outputs for four GPT configurations whose original logs are unavailable; never substitutes for published scores.",
                "retains_annotated_history": True, "models": {m: "codex" for m in MODELS},
                "repeats": 3, "problems": inputs, "snapshot_sha256": provenance["snapshot_sha256"],
                "runner_source": str(runner), "workers": 6,
                "authorization": "Latest request explicitly asks for scene accuracy with and without history information."}
    existing = root / "protocol.json"
    if existing.exists() and json.loads(existing.read_text()) != protocol:
        raise ValueError("Supplement protocol changed")
    for pid, files in inputs.items():
        for name, expected in files.items():
            source = repo / "bench/problems" / pid / name
            target = root / "problems" / pid / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if "symlink" in expected:
                if not source.is_symlink() or str(source.readlink()) != expected["symlink"]:
                    raise ValueError("Original current-state link changed")
                if not target.is_symlink():
                    target.symlink_to(expected["symlink"])
                if str(target.readlink()) != expected["symlink"]:
                    raise ValueError("Supplement current-state link changed")
            else:
                if digest(source) != expected["sha256"]:
                    raise ValueError(f"Original input changed: {pid}/{name}")
                if not target.exists():
                    shutil.copyfile(source, target)
                if digest(target) != expected["sha256"]:
                    raise ValueError("Supplement input changed")
    dump(existing, protocol)
    return protocol


def run_trial(runner: Path, root: Path, model: str, problem: str, repeat: int) -> dict:
    """Run one original GPT invocation and preserve its raw result without retries.

    Args:
        runner (Path): Exact paper GPT source snapshot.
        root (Path): Annotated supplement output root.
        model (str): Requested GPT model ID.
        problem (str): Original problem ID.
        repeat (int): Repetition index in 1..3.

    Returns:
        dict: Canonical wrapper result and full output location.
    """
    trial = root / "records" / model / f"repeat_{repeat}" / problem
    record_path = trial / "record.json"
    if record_path.exists():
        return json.loads(record_path.read_text())
    attempt = trial / "attempt_1"
    attempt.mkdir(parents=True)
    run_id = f"{problem}_codex_native_withann_supplement_{model}_r{repeat}_a1"
    cmd = command(runner, root, model, problem, run_id)
    dump(attempt / "launch.json", {"command": cmd, "started_unix": time.time()})
    with (attempt / "stdout.txt").open("w") as stdout, (attempt / "stderr.txt").open("w") as stderr:
        result = subprocess.run(cmd, cwd=runner, stdout=stdout, stderr=stderr, check=False)
    try:
        wrapper = json.loads((attempt / "stdout.txt").read_text())
    except ValueError:
        wrapper = None
    record = {"model": model, "problem": problem, "repeat": repeat, "attempt": 1,
              "status": (wrapper or {}).get("status", "wrapper_failed"), "returncode": result.returncode,
              "run_id": run_id, "run_dir": str(root / "problems" / problem / "runs" / run_id),
              "wrapper_result": wrapper, "finished_unix": time.time(), "annotated_history": True}
    dump(attempt / "record.json", record)
    dump(record_path, record)
    print("RESULT", model, problem, repeat, record["status"], flush=True)
    return record


def main() -> None:
    """Run a six-slot annotated supplement, stopping after any transport failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "baseline", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    protocol = prepare(args.repo, args.baseline, args.output)
    if args.prepare_only:
        print("PREPARED", args.output)
        return
    root = args.output
    with (root / "codex.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        jobs = [(m, f"p{p}", r) for r in range(1, 4) for p in range(1, 37) for m in MODELS
                if not (root / "records" / m / f"repeat_{r}" / f"p{p}" / "record.json").exists()]
        remaining = len(jobs)

        def progress(row: dict) -> None:
            """Persist returned trial progress; row (dict) is already on disk."""
            nonlocal remaining
            remaining -= 1
            dump(root / "codex_status.json", {"pending": remaining, "workers": 6, "updated_unix": time.time()})

        dump(root / "codex_status.json", {"pending": remaining, "workers": 6, "updated_unix": time.time()})
        rows = rolling_map(jobs, lambda job: run_trial(Path(protocol["runner_source"]), root, *job), 6,
                           lambda row: row["status"] not in {"ok", "invalid_outputs"}, progress)
        if any(row["status"] not in {"ok", "invalid_outputs"} for row in rows):
            raise RuntimeError("Transport failure; inspect retained outputs before continuing")
        print("QUEUE_FINISHED annotated_gpt", flush=True)


if __name__ == "__main__":
    main()
