#!/usr/bin/env python3
"""Normalize old perception run reports with the local Codex normalizer agent."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBLEMS_DIR = ROOT / "bench" / "problems"
DEFAULT_BATCH_IDS = (
    "batch003_gpt54mini_split_low_codex_native_gpt5_4_mini_medium_split",
    "batch004_gpt55low_split_low_codex_native_gpt5_5_low_split",
    "batch006_gpt54medium_split_low_codex_native_gpt5_4_medium_split",
    "batch008_gpt55medium_split_low_codex_native_gpt5_5_medium_split",
    "batch009_gpt55high_split_low_codex_native_gpt5_5_high_split",
)
NORMALIZER_AGENT = ROOT / ".codex" / "agents" / "report_normalizer_agent.toml"


PROMPT_TEMPLATE = """Use report_normalizer_agent to normalize this old DexHoldem perception run.

Important boundaries:
- This is post-processing only.
- Do not inspect images.
- Do not inspect benchmark ground truth or problem labels.
- Use only files under this workspace.
- Return strict JSON only.

Run metadata:
- problem_id: {problem_id}
- run_id: {run_id}

Input files are copied into this workspace. Write the final strict JSON to:
normalized_visual_summary.json
"""


def load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def batch_run_ids(batch_dir: Path) -> list[tuple[str, str]]:
    manifest = load_json(batch_dir / "manifest.json")
    variant = manifest["visual_variant"]
    setting = manifest["visual_setting"]
    prefix = manifest["run_prefix"]
    return [(f"p{i}", f"p{i}_{variant}_{setting}_{prefix}") for i in range(1, 37)]


def copy_if_exists(src: Path, dest: Path) -> None:
    if src.exists():
        if src.is_dir():
            shutil.copytree(src, dest, symlinks=True)
        else:
            shutil.copy2(src, dest)


def build_workspace(run_dir: Path, workspace: Path) -> None:
    for name in (
        "visual_summary.json",
        "eval_report.md",
        "output_check.json",
        "harness_prompt.md",
        "harness_version.json",
        "agent_manifest.json",
    ):
        copy_if_exists(run_dir / name, workspace / name)
    copy_if_exists(run_dir / "visual_raw", workspace / "visual_raw")
    agent_dest = workspace / ".codex" / "agents"
    agent_dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(NORMALIZER_AGENT, agent_dest / NORMALIZER_AGENT.name)


def extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start < 0:
            raise
        decoder = json.JSONDecoder()
        normalized, _ = decoder.raw_decode(text[start:])
        if not isinstance(normalized, dict):
            raise ValueError("normalized output must be a JSON object")
        return normalized


def normalize_one(args: argparse.Namespace, problem_id: str, run_id: str) -> dict:
    run_dir = PROBLEMS_DIR / problem_id / "runs" / run_id
    if not run_dir.exists():
        return {"problem_id": problem_id, "run_id": run_id, "status": "missing_run_dir"}

    output_path = run_dir / args.output_name
    if output_path.exists() and args.skip_existing:
        return {"problem_id": problem_id, "run_id": run_id, "status": "skipped_existing"}

    with tempfile.TemporaryDirectory(prefix=f"normalize_{problem_id}_") as tmp:
        workspace = Path(tmp)
        build_workspace(run_dir, workspace)
        prompt = PROMPT_TEMPLATE.format(problem_id=problem_id, run_id=run_id)
        cmd = [
            args.codex_bin,
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "-C",
            str(workspace),
            prompt,
        ]
        env = os.environ.copy()
        result = subprocess.run(cmd, cwd=workspace, capture_output=True, text=True, env=env)
        log_dir = run_dir / "normalizer_logs"
        log_dir.mkdir(exist_ok=True)
        (log_dir / f"{args.output_name}.stdout.txt").write_text(result.stdout)
        (log_dir / f"{args.output_name}.stderr.txt").write_text(result.stderr)
        (log_dir / f"{args.output_name}.exit.json").write_text(
            json.dumps({"returncode": result.returncode, "cmd": cmd}, indent=2) + "\n"
        )
        if result.returncode != 0:
            return {
                "problem_id": problem_id,
                "run_id": run_id,
                "status": "codex_failed",
                "returncode": result.returncode,
            }

        candidate = workspace / "normalized_visual_summary.json"
        try:
            if candidate.exists():
                normalized = extract_json(candidate.read_text())
            else:
                normalized = extract_json(result.stdout)
        except Exception as exc:  # noqa: BLE001
            return {
                "problem_id": problem_id,
                "run_id": run_id,
                "status": "bad_normalized_json",
                "error": str(exc),
            }
        output_path.write_text(json.dumps(normalized, indent=2) + "\n")
        return {"problem_id": problem_id, "run_id": run_id, "status": "ok", "output": str(output_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch-dir",
        action="append",
        help="Batch dir to normalize. Defaults to the six completed Codex split batches.",
    )
    parser.add_argument("--problem-list", help="Comma-separated problem ids, e.g. p1,p2. Default: all p1-p36.")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--output-name", default="normalized_visual_summary.json")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--concurrency", type=int, default=6, help="Number of simultaneous Codex normalizer calls.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be at least 1")

    batch_dirs = [Path(p).resolve() for p in args.batch_dir] if args.batch_dir else [
        ROOT / "perception_eval" / "batch_runs" / batch_id for batch_id in DEFAULT_BATCH_IDS
    ]
    problem_filter = set(args.problem_list.split(",")) if args.problem_list else None

    jobs: list[tuple[str, str]] = []
    for batch_dir in batch_dirs:
        for problem_id, run_id in batch_run_ids(batch_dir):
            if problem_filter and problem_id not in problem_filter:
                continue
            jobs.append((problem_id, run_id))

    if args.dry_run:
        print(json.dumps({"jobs": len(jobs), "first_jobs": jobs[:10]}, indent=2))
        return

    results = []
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        future_map = {
            executor.submit(normalize_one, args, problem_id, run_id): (problem_id, run_id)
            for problem_id, run_id in jobs
        }
        for future in concurrent.futures.as_completed(future_map):
            completed += 1
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001
                problem_id, run_id = future_map[future]
                result = {
                    "problem_id": problem_id,
                    "run_id": run_id,
                    "status": "normalizer_exception",
                    "error": str(exc),
                }
            results.append(result)
            print(json.dumps({"index": completed, "total": len(jobs), **result}), flush=True)

    summary = {
        "total": len(results),
        "ok": sum(1 for result in results if result["status"] == "ok"),
        "skipped_existing": sum(1 for result in results if result["status"] == "skipped_existing"),
        "failures": [result for result in results if result["status"] not in {"ok", "skipped_existing"}],
    }
    print(json.dumps(summary, indent=2))
    if summary["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
