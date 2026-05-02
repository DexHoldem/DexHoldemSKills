#!/usr/bin/env python3
"""Run perception benchmarks over many problems with a fixed concurrency buffer."""

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
RUN_CODEX = ROOT / "perception_eval" / "run_codex_benchmark.py"
RUN_CLAUDE = ROOT / "perception_eval" / "run_claude_benchmark.py"
DEFAULT_BATCH_ROOT = ROOT / "perception_eval" / "batch_runs"


def requires_openrouter(visual_variant: str) -> bool:
    return visual_variant.startswith(("codex_openrouter_", "claude_openrouter_"))


def runner_for_variant(visual_variant: str) -> Path:
    if visual_variant.startswith("claude"):
        return RUN_CLAUDE
    return RUN_CODEX


def sanitize(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def problem_number(path: Path) -> int | None:
    if not path.name.startswith("p"):
        return None
    suffix = path.name[1:]
    return int(suffix) if suffix.isdigit() else None


def parse_problem_names(text: str) -> list[str]:
    return [item.strip() for item in re.split(r"[\s,]+", text) if item.strip()]


def discover_problems(args: argparse.Namespace) -> list[Path]:
    root = Path(args.problems_root).resolve()
    if args.problem_list and args.problem_list_file:
        raise SystemExit("use only one of --problem-list or --problem-list-file")
    if args.problem_list or args.problem_list_file:
        if args.problem_list_file:
            names = parse_problem_names(Path(args.problem_list_file).read_text())
        else:
            names = parse_problem_names(args.problem_list)
        problems = [root / name for name in names]
    else:
        problems = []
        for path in root.iterdir():
            if not path.is_dir():
                continue
            number = problem_number(path)
            if number is None:
                continue
            if args.problem_start <= number <= args.problem_end:
                problems.append(path)
        problems.sort(key=lambda path: problem_number(path) or 0)

    missing = [str(path) for path in problems if not path.is_dir()]
    if missing:
        raise SystemExit(f"missing problem dirs: {', '.join(missing)}")
    return problems


def load_existing_ok(problem: Path, run_id: str) -> bool:
    output_check = problem / "runs" / run_id / "output_check.json"
    if not output_check.exists():
        return False
    try:
        return bool(json.loads(output_check.read_text()).get("ok"))
    except json.JSONDecodeError:
        return False


def build_command(args: argparse.Namespace, problem: Path, run_id: str) -> list[str]:
    cmd = [
        sys.executable,
        str(runner_for_variant(args.visual_variant)),
        "--problem-dir",
        str(problem),
        "--visual-setting",
        args.visual_setting,
        "--visual-variant",
        args.visual_variant,
        "--run-id",
        run_id,
        "--model",
        args.model,
        "--reasoning-effort",
        args.reasoning_effort,
        "--agent-max-threads",
        str(args.agent_max_threads),
    ]
    if not args.visual_variant.startswith("claude"):
        cmd.extend(["--service-tier", args.service_tier])
    if args.no_isolated_workspace:
        cmd.append("--no-isolated-workspace")
    if args.keep_isolated_workspace:
        cmd.append("--keep-isolated-workspace")
    if args.isolation_root:
        cmd.extend(["--isolation-root", args.isolation_root])
    if args.keep_installed:
        cmd.append("--keep-installed")
    if args.no_clean_before:
        cmd.append("--no-clean-before")
    if args.extra_runner_arg:
        for item in args.extra_runner_arg:
            cmd.extend(item.split())
    return cmd


def append_jsonl(path: Path, record: dict) -> None:
    with path.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


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
            return json.loads(text[start + 1 :])
        except json.JSONDecodeError:
            return None


def provider_limit_message(record: dict) -> str | None:
    runner_result = record.get("runner_result")
    if not isinstance(runner_result, dict):
        return None
    run_dir = runner_result.get("run_dir")
    if not run_dir:
        return None

    for name in ("claude_stdout.txt", "claude_stderr.txt", "codex_stdout.txt", "codex_stderr.txt"):
        path = Path(run_dir) / name
        if not path.exists():
            continue
        text = path.read_text(errors="replace")
        if "api_error_status\":429" in text or "api_error_status\": 429" in text or "You've hit your limit" in text:
            return "provider_limit_429"
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--visual-variant", required=True)
    parser.add_argument("--visual-setting", choices=("split", "general"), default="split")
    parser.add_argument("--problems-root", default=str(ROOT / "bench" / "problems"))
    parser.add_argument("--problem-start", type=int, default=1)
    parser.add_argument("--problem-end", type=int, default=36)
    parser.add_argument("--problem-list", help="Comma-separated problem names, e.g. p1,p3,p8")
    parser.add_argument("--problem-list-file", help="File containing problem names separated by commas or whitespace")
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--reasoning-effort", default="low")
    parser.add_argument("--service-tier", default="fast")
    parser.add_argument("--agent-max-threads", type=int, default=9)
    parser.add_argument("--run-prefix", help="Batch run prefix. Default is timestamped.")
    parser.add_argument("--batch-root", default=str(DEFAULT_BATCH_ROOT))
    parser.add_argument("--isolation-root")
    parser.add_argument("--no-isolated-workspace", action="store_true")
    parser.add_argument("--keep-isolated-workspace", action="store_true")
    parser.add_argument("--keep-installed", action="store_true")
    parser.add_argument("--no-clean-before", action="store_true")
    parser.add_argument("--skip-existing-ok", action="store_true")
    parser.add_argument("--allow-failures", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print selected commands without launching subprocesses.")
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument(
        "--extra-runner-arg",
        action="append",
        help="Extra argument string appended to each run_codex_benchmark.py command.",
    )
    args = parser.parse_args()

    if args.concurrency < 1:
        raise SystemExit("--concurrency must be at least 1")
    if requires_openrouter(args.visual_variant) and not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit(
            f"{args.visual_variant} requires OPENROUTER_API_KEY. "
            "Set it before launching this batch, or skip OpenRouter variants."
        )

    problems = discover_problems(args)
    if not problems:
        raise SystemExit("no problems selected")

    run_prefix = sanitize(args.run_prefix or time.strftime("%Y%m%d_%H%M%S"))
    variant_slug = sanitize(args.visual_variant)
    setting_slug = sanitize(args.visual_setting)
    batch_id = sanitize(f"{run_prefix}_{variant_slug}_{setting_slug}")
    batch_dir = Path(args.batch_root).resolve() / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)
    events_path = batch_dir / "events.jsonl"
    summary_path = batch_dir / "summary.json"

    queued: list[dict] = []
    skipped: list[dict] = []
    for problem in problems:
        run_id = sanitize(f"{problem.name}_{variant_slug}_{setting_slug}_{run_prefix}")
        if args.skip_existing_ok and load_existing_ok(problem, run_id):
            skipped.append({"problem": problem.name, "run_id": run_id, "status": "skipped_existing_ok"})
            continue
        queued.append({
            "problem": problem,
            "problem_name": problem.name,
            "run_id": run_id,
            "cmd": build_command(args, problem, run_id),
        })

    manifest = {
        "batch_id": batch_id,
        "visual_variant": args.visual_variant,
        "visual_setting": args.visual_setting,
        "concurrency": args.concurrency,
        "model": args.model,
        "reasoning_effort": args.reasoning_effort,
        "service_tier": None if args.visual_variant.startswith("claude") else args.service_tier,
        "problem_count": len(problems),
        "queued_count": len(queued),
        "skipped_count": len(skipped),
        "run_prefix": run_prefix,
        "batch_dir": str(batch_dir),
    }
    (batch_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for item in skipped:
        append_jsonl(events_path, {**item, "event": "skipped", "time": time.time()})

    if args.dry_run:
        dry_run = {
            **manifest,
            "event": "dry_run",
            "commands": [
                {
                    "problem": item["problem_name"],
                    "run_id": item["run_id"],
                    "cmd": item["cmd"],
                }
                for item in queued
            ],
            "skipped": skipped,
        }
        (batch_dir / "dry_run.json").write_text(json.dumps(dry_run, indent=2) + "\n")
        print(json.dumps(dry_run, indent=2), flush=True)
        return

    pending = list(queued)
    active: list[dict] = []
    completed: list[dict] = []
    halted_reason = None
    started = time.time()

    print(json.dumps({**manifest, "event": "batch_start"}, indent=2), flush=True)

    while pending or active:
        while pending and len(active) < args.concurrency:
            item = pending.pop(0)
            launch_time = time.time()
            proc = subprocess.Popen(
                item["cmd"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy(),
            )
            active.append({**item, "proc": proc, "started_at": launch_time})
            event = {
                "event": "started",
                "time": launch_time,
                "problem": item["problem_name"],
                "run_id": item["run_id"],
                "pid": proc.pid,
                "active": len(active),
                "remaining": len(pending),
            }
            append_jsonl(events_path, event)
            print(json.dumps(event), flush=True)

        still_active: list[dict] = []
        for item in active:
            proc = item["proc"]
            if proc.poll() is None:
                still_active.append(item)
                continue
            stdout, stderr = proc.communicate()
            ended = time.time()
            runner_json = parse_runner_json(stdout)
            stdout_path = batch_dir / f"{item['run_id']}.stdout.txt"
            stderr_path = batch_dir / f"{item['run_id']}.stderr.txt"
            stdout_path.write_text(stdout)
            stderr_path.write_text(stderr)
            record = {
                "event": "finished",
                "time": ended,
                "problem": item["problem_name"],
                "run_id": item["run_id"],
                "returncode": proc.returncode,
                "duration_s": round(ended - item["started_at"], 3),
                "stdout_log": str(stdout_path),
                "stderr_log": str(stderr_path),
                "runner_result": runner_json,
            }
            completed.append(record)
            append_jsonl(events_path, record)
            print(json.dumps(record), flush=True)
            limit_reason = provider_limit_message(record)
            if limit_reason and halted_reason is None:
                halted_reason = limit_reason
                dropped = [
                    {"problem": pending_item["problem_name"], "run_id": pending_item["run_id"]}
                    for pending_item in pending
                ]
                event = {
                    "event": "halted",
                    "time": time.time(),
                    "reason": halted_reason,
                    "pending_count": len(pending),
                    "pending": dropped,
                }
                pending.clear()
                append_jsonl(events_path, event)
                print(json.dumps(event), flush=True)
        active = still_active
        if active:
            time.sleep(args.poll_interval)

    failures = [
        item for item in completed
        if item["returncode"] != 0
        or not isinstance(item.get("runner_result"), dict)
        or item["runner_result"].get("status") != "ok"
    ]
    summary = {
        **manifest,
        "duration_s": round(time.time() - started, 3),
        "completed_count": len(completed),
        "failure_count": len(failures),
        "halted_reason": halted_reason,
        "failures": [
            {
                "problem": item["problem"],
                "run_id": item["run_id"],
                "returncode": item["returncode"],
                "runner_status": (item.get("runner_result") or {}).get("status")
                if isinstance(item.get("runner_result"), dict)
                else None,
            }
            for item in failures
        ],
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({**summary, "event": "batch_done"}, indent=2), flush=True)
    if failures and not args.allow_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
