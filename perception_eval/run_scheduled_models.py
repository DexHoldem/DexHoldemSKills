#!/usr/bin/env python3
"""Schedule perception benchmark runs across multiple Claude models, paced over a time window.

Distributes runs uniformly so that API rate limits (which reset on fixed
boundaries) are not exhausted in a single burst.  Supports round-robin
interleaving across models and automatic sleep between target start times.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_CLAUDE = ROOT / "perception_eval" / "run_claude_benchmark.py"
BATCH_ROOT = ROOT / "perception_eval" / "batch_runs"


def sanitize(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def discover_problems(root: Path, start: int, end: int) -> list[Path]:
    problems = []
    for p in root.iterdir():
        if p.is_dir() and p.name.startswith("p"):
            suffix = p.name[1:]
            if suffix.isdigit() and start <= int(suffix) <= end:
                problems.append(p)
    problems.sort(key=lambda p: int(p.name[1:]))
    return problems


def load_existing_ok(problem: Path, run_id: str) -> bool:
    output_check = problem / "runs" / run_id / "output_check.json"
    if not output_check.exists():
        return False
    try:
        return bool(json.loads(output_check.read_text()).get("ok"))
    except (json.JSONDecodeError, KeyError):
        return False


def fmt_duration(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"


def parse_runner_json(stdout: str) -> dict | None:
    text = stdout.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.rfind("\n{")
        if start == -1:
            return None
        try:
            return json.loads(text[start + 1:])
        except json.JSONDecodeError:
            return None


def detect_rate_limit(stdout: str, stderr: str) -> bool:
    for text in (stdout, stderr):
        if "api_error_status\":429" in text or "api_error_status\": 429" in text:
            return True
        if "You've hit your limit" in text:
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models", nargs="+", required=True,
        help="Model IDs, e.g. claude-opus-4-6 claude-opus-4-7 claude-sonnet-4-6",
    )
    parser.add_argument("--duration-hours", type=float, default=10.0, help="Total time window in hours")
    parser.add_argument("--problems-root", default=str(ROOT / "bench" / "problems"))
    parser.add_argument("--problem-start", type=int, default=1)
    parser.add_argument("--problem-end", type=int, default=36)
    parser.add_argument("--skill", default="v2-native")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--concurrency", type=int, default=2, help="Max concurrent runs (default 2; minimum 2 for 108 runs × ~10 min in 10h)")
    parser.add_argument("--skip-existing-ok", action="store_true", help="Skip runs that already have ok output_check")
    parser.add_argument("--run-prefix", help="Override run prefix (default: timestamped)")
    parser.add_argument(
        "--interleave", choices=("round-robin", "sequential"), default="round-robin",
        help="round-robin alternates models per problem; sequential finishes all problems per model first",
    )
    parser.add_argument("--rate-limit-pause", type=float, default=300,
                        help="Seconds to pause when a 429 rate limit is detected (default 300)")
    parser.add_argument("--dry-run", action="store_true", help="Print schedule without launching runs")
    parser.add_argument("--log-file", help="Append JSONL events to this file")
    args = parser.parse_args()

    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1")

    problems_root = Path(args.problems_root).resolve()
    problems = discover_problems(problems_root, args.problem_start, args.problem_end)
    if not problems:
        raise SystemExit("no problems found")

    run_prefix = sanitize(args.run_prefix or time.strftime("%Y%m%d_%H%M%S"))

    runs_by_model: dict[str, list[dict]] = {m: [] for m in args.models}
    for model in args.models:
        model_slug = sanitize(model)
        for problem in problems:
            run_id = f"{problem.name}_{model_slug}_native_native_{run_prefix}"
            runs_by_model[model].append({
                "model": model,
                "model_slug": model_slug,
                "problem": problem,
                "problem_name": problem.name,
                "run_id": run_id,
            })

    if args.interleave == "round-robin":
        runs: list[dict] = []
        max_len = max(len(v) for v in runs_by_model.values())
        for i in range(max_len):
            for m in args.models:
                if i < len(runs_by_model[m]):
                    runs.append(runs_by_model[m][i])
    else:
        runs = []
        for m in args.models:
            runs.extend(runs_by_model[m])

    if args.skip_existing_ok:
        before = len(runs)
        runs = [r for r in runs if not load_existing_ok(r["problem"], r["run_id"])]
        skipped = before - len(runs)
        if skipped:
            print(f"Skipped {skipped} already-completed runs", flush=True)

    total_runs = len(runs)
    if total_runs == 0:
        print("All runs already completed. Nothing to do.")
        return

    duration_s = args.duration_hours * 3600
    interval_s = duration_s / total_runs if total_runs > 1 else 0

    print(f"Schedule: {total_runs} runs over {args.duration_hours}h "
          f"(target ~{interval_s:.0f}s between starts)")
    print(f"  Models: {', '.join(args.models)}")
    print(f"  Problems: p{args.problem_start}..p{args.problem_end} ({len(problems)} problems)")
    print(f"  Interleave: {args.interleave}, concurrency: {args.concurrency}")
    print(f"  Run prefix: {run_prefix}")
    print(flush=True)

    if args.dry_run:
        for i, r in enumerate(runs):
            target_offset = i * interval_s
            print(f"  [{i + 1:3d}/{total_runs}] +{fmt_duration(target_offset)}  "
                  f"{r['model']:25s}  {r['problem_name']:5s}  run_id={r['run_id']}")
        return

    log_file = Path(args.log_file) if args.log_file else None
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_event(event: dict) -> None:
        if log_file:
            with log_file.open("a") as f:
                f.write(json.dumps(event, sort_keys=True) + "\n")

    batch_start = time.time()
    log_event({
        "event": "schedule_start",
        "time": batch_start,
        "total_runs": total_runs,
        "duration_hours": args.duration_hours,
        "interval_s": round(interval_s, 1),
        "models": args.models,
        "interleave": args.interleave,
        "concurrency": args.concurrency,
        "run_prefix": run_prefix,
    })

    active: list[dict] = []
    completed_count = 0
    failure_count = 0

    def drain_finished() -> None:
        nonlocal completed_count, failure_count
        still_active: list[dict] = []
        for a in active:
            proc = a["proc"]
            if proc.poll() is None:
                still_active.append(a)
                continue
            stdout, stderr = proc.communicate()
            rc = proc.returncode
            elapsed = time.time() - a["started_at"]
            runner_result = parse_runner_json(stdout)
            status = "ok"
            if rc != 0:
                status = "FAILED"
            elif isinstance(runner_result, dict) and runner_result.get("status") != "ok":
                status = runner_result.get("status", "unknown")

            completed_count += 1
            if status != "ok":
                failure_count += 1

            hit_limit = detect_rate_limit(stdout, stderr)
            print(f"  Done [{completed_count}/{total_runs}] {a['problem_name']} "
                  f"model={a['model']} rc={rc} status={status} "
                  f"[{elapsed:.0f}s]{' *** RATE LIMITED ***' if hit_limit else ''}",
                  flush=True)
            log_event({
                "event": "finished",
                "time": time.time(),
                "problem": a["problem_name"],
                "model": a["model"],
                "run_id": a["run_id"],
                "returncode": rc,
                "status": status,
                "duration_s": round(elapsed, 1),
                "rate_limited": hit_limit,
            })

            if hit_limit:
                print(f"  Rate limit detected — pausing {args.rate_limit_pause:.0f}s...", flush=True)
                time.sleep(args.rate_limit_pause)

        active[:] = still_active

    for i, run in enumerate(runs):
        target_start = batch_start + i * interval_s
        now = time.time()
        if now < target_start:
            wait = target_start - now
            print(f"[{i + 1}/{total_runs}] Waiting {fmt_duration(wait)} until next slot...", flush=True)
            while time.time() < target_start:
                drain_finished()
                remaining = target_start - time.time()
                if remaining > 0:
                    time.sleep(min(remaining, 5.0))

        while len(active) >= args.concurrency:
            drain_finished()
            if len(active) >= args.concurrency:
                time.sleep(2)

        cmd = [
            sys.executable, str(RUN_CLAUDE),
            "--problem-dir", str(run["problem"]),
            "--skill", args.skill,
            "--run-id", run["run_id"],
            "--model", run["model"],
            "--reasoning-effort", args.reasoning_effort,
        ]
        print(f"[{i + 1}/{total_runs}] Starting {run['problem_name']} model={run['model']}  "
              f"(+{fmt_duration(time.time() - batch_start)} elapsed)", flush=True)
        proc = subprocess.Popen(
            cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=os.environ.copy(),
        )
        active.append({**run, "proc": proc, "started_at": time.time()})
        log_event({
            "event": "started",
            "time": time.time(),
            "problem": run["problem_name"],
            "model": run["model"],
            "run_id": run["run_id"],
            "pid": proc.pid,
            "slot": i + 1,
        })

    while active:
        drain_finished()
        if active:
            time.sleep(2)

    total_elapsed = time.time() - batch_start
    summary = (f"\nDone: {completed_count}/{total_runs} completed, "
               f"{failure_count} failures, elapsed {fmt_duration(total_elapsed)}")
    print(summary, flush=True)
    log_event({
        "event": "schedule_done",
        "time": time.time(),
        "total_runs": total_runs,
        "completed": completed_count,
        "failures": failure_count,
        "elapsed_s": round(total_elapsed, 1),
    })

    if failure_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
