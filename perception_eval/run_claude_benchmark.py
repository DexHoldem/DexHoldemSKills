#!/usr/bin/env python3
"""Run one Claude perception benchmark: preflight -> claude -p -> cleanup."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from default_prompt import DEFAULT_PROMPT


SCRIPT_DIR = Path(__file__).resolve().parent
PREFLIGHT = SCRIPT_DIR / "preflight.py"
DEFAULT_ISOLATION_ROOT = SCRIPT_DIR.parent.parent / ".dexholdem_perception_eval_work"

ACTIVE_INSTALL_NAMES = {
    ".codex",
    ".claude",
    "action_translator.py",
    "capture.py",
    "executor.py",
    "preflight.py",
    "remote_exec.py",
    "router.py",
    "state.py",
    "text_to_sound.py",
    "utils.py",
    "config.yaml",
    "pyproject.toml",
    "visual_guidelines",
}


def requires_openrouter(visual_variant: str) -> bool:
    return visual_variant.startswith("claude_openrouter_")


def run_json(cmd: list[str], *, cwd: Path | None = None) -> dict:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {shlex.join(cmd)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command did not return JSON: {shlex.join(cmd)}\n{result.stdout}") from exc


def file_record(path: Path, base: Path) -> dict:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "path": str(path.relative_to(base)),
        "sha256": digest.hexdigest(),
        "size": path.stat().st_size,
    }


def command_version(cmd: list[str]) -> dict:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "cmd": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def cleanup(problem_dir: Path, *, dry_run: bool) -> dict:
    cmd = [sys.executable, str(PREFLIGHT), "--cleanup", "--problem-dir", str(problem_dir)]
    if dry_run:
        cmd.append("--dry-run")
    return run_json(cmd)


def isolation_ignore(_dir: str, names: list[str]) -> set[str]:
    ignored = {"runs", "__pycache__"}
    ignored.update(name for name in names if name in ACTIVE_INSTALL_NAMES)
    return ignored


def create_isolated_problem_copy(problem_dir: Path, run_id: str, isolation_root: Path) -> tuple[Path, Path]:
    isolation_root.mkdir(parents=True, exist_ok=True)
    parent = Path(tempfile.mkdtemp(prefix=f"{problem_dir.name}_{run_id}_", dir=isolation_root))
    isolated_problem_dir = parent / problem_dir.name
    shutil.copytree(problem_dir, isolated_problem_dir, symlinks=True, ignore=isolation_ignore)
    return parent, isolated_problem_dir


def copy_run_artifacts(src_run_dir: Path, dest_run_dir: Path) -> None:
    dest_run_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(src_run_dir.iterdir()):
        dest = dest_run_dir / path.name
        if path.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(path, dest, symlinks=True)
        else:
            shutil.copy2(path, dest)


def run_has_perception_outputs(candidate: Path) -> bool:
    visual_raw_dir = candidate / "visual_raw"
    return (
        (candidate / "visual_summary.json").exists()
        and (candidate / "eval_report.md").exists()
        and visual_raw_dir.is_dir()
        and any(path.is_file() for path in visual_raw_dir.iterdir())
    )


def recover_misnamed_outputs(run_dir: Path) -> dict | None:
    if run_has_perception_outputs(run_dir):
        return None

    candidates = [
        path
        for path in sorted(run_dir.parent.iterdir())
        if path.is_dir() and path != run_dir and run_has_perception_outputs(path)
    ]
    if len(candidates) != 1:
        return {
            "status": "not_recovered",
            "candidate_count": len(candidates),
            "candidates": [str(path) for path in candidates],
        } if candidates else None

    source = candidates[0]
    recovered = []
    for name in ("visual_raw", "visual_summary.json", "eval_report.md"):
        src = source / name
        dest = run_dir / name
        if src.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest, symlinks=True)
        elif src.is_file():
            shutil.copy2(src, dest)
        recovered.append(name)

    result = {
        "status": "recovered",
        "source_run_dir": str(source),
        "expected_run_dir": str(run_dir),
        "recovered": recovered,
    }
    (run_dir / "output_recovery.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def valid_chip_counts(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if set(value) != {"5", "10", "50", "100"}:
        return False
    return all(isinstance(item, int) and not isinstance(item, bool) for item in value.values())


def valid_bool(value: object) -> bool:
    return isinstance(value, bool)


def visual_summary_schema_errors(summary: object) -> list[str]:
    """Validate visual_summary.json against nested schema (table.* fields)."""
    if not isinstance(summary, dict):
        return ["summary_not_object"]

    errors = []
    allowed_stage = {"idle", "acting", "atom_idle", "down", "to_recover", "win", "lose", "show_hand"}
    allowed_blind = {"big_blind", "small_blind", "none"}
    allowed_outcome = {"win", "lose", "tie", "not_showdown"}

    if summary.get("loop_stage") not in allowed_stage:
        errors.append("loop_stage")
    if summary.get("blind") not in allowed_blind:
        errors.append("blind")
    if summary.get("showdown_outcome") not in allowed_outcome:
        errors.append("showdown_outcome")

    table = summary.get("table", {})
    if not isinstance(table, dict):
        errors.append("table")
        return errors

    if not valid_bool(table.get("scene_stable")):
        errors.append("table.scene_stable")
    if not valid_bool(table.get("is_my_turn")):
        errors.append("table.is_my_turn")
    if not isinstance(table.get("community_cards"), list):
        errors.append("table.community_cards")
    for key in ("my_chips", "opponent_chips", "my_current_bet", "opponent_bet"):
        if not valid_chip_counts(table.get(key)):
            errors.append(f"table.{key}")
    if not isinstance(table.get("uncertain_fields"), list):
        errors.append("table.uncertain_fields")
    return errors


def verify_run_outputs(run_dir: Path) -> dict:
    visual_raw_dir = run_dir / "visual_raw"
    raw_files = sorted(path.relative_to(run_dir).as_posix() for path in visual_raw_dir.glob("*") if path.is_file())
    summary_path = run_dir / "visual_summary.json"
    blocked_summary = False
    summary_parse_error = None
    schema_errors = ["missing_visual_summary"]
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text())
            blocked_summary = isinstance(summary, dict) and summary.get("status") == "blocked"
            schema_errors = visual_summary_schema_errors(summary)
        except json.JSONDecodeError as exc:
            summary_parse_error = str(exc)
            schema_errors = ["bad_visual_summary_json"]
    required = {
        "visual_summary": summary_path.exists(),
        "visual_summary_schema": not schema_errors,
        "eval_report": (run_dir / "eval_report.md").exists(),
        "visual_raw_dir": visual_raw_dir.is_dir(),
        "visual_raw_files": bool(raw_files),
        "not_blocked": not blocked_summary,
    }
    result = {
        "ok": all(required.values()),
        "required": required,
        "visual_raw_files": raw_files,
        "blocked_summary": blocked_summary,
    }
    if summary_parse_error is not None:
        result["summary_parse_error"] = summary_parse_error
    if schema_errors:
        result["visual_summary_schema_errors"] = schema_errors
    return result


def wrapper_version(args: argparse.Namespace) -> dict:
    return {
        "runner_script": file_record(Path(__file__).resolve(), SCRIPT_DIR.parent),
        "preflight_script": file_record(PREFLIGHT.resolve(), SCRIPT_DIR.parent),
        "claude_version": command_version([args.claude_bin, "--version"]),
        "python_version": command_version([sys.executable, "--version"]),
        "model": args.model,
        "effort": args.reasoning_effort,
        "permission_mode": args.permission_mode,
        "isolated_workspace": not args.no_isolated_workspace,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem-dir", required=True, help="Problem folder, e.g. bench/problems/p3")
    parser.add_argument("--skill", choices=("v2", "v2-native"), default="v2", help="Skill: v2 (subagents) or v2-native (no subagents)")
    parser.add_argument("--visual-setting", choices=("general", "split"), default="split", help="Visual setting (v2 only)")
    parser.add_argument("--visual-variant", help="Variant under subagent/ (v2 only), e.g. claude_opus_4_7_medium")
    parser.add_argument("--run-id", required=True, help="Run folder name under problem_dir/runs/")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--reasoning-effort", default="low", choices=("low", "medium", "high", "xhigh", "max"))
    parser.add_argument("--service-tier", default="fast", help="Accepted for parity with Codex runner; unused by Claude.")
    parser.add_argument("--agent-max-threads", type=int, default=9, help="Accepted for parity with Codex runner; unused by Claude.")
    parser.add_argument("--permission-mode", default="acceptEdits")
    parser.add_argument("--prompt", help="Inline prompt for claude -p. Defaults to the benchmark prompt.")
    parser.add_argument("--prompt-file", help="Read claude -p prompt from this file.")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--keep-installed", action="store_true", help="Do not cleanup active install after claude exits")
    parser.add_argument("--no-clean-before", action="store_true", help="Do not ask preflight to clean previous install first")
    parser.add_argument(
        "--no-isolated-workspace",
        action="store_true",
        help="Run directly inside --problem-dir. Default creates an isolated problem copy without previous runs/.",
    )
    parser.add_argument(
        "--isolation-root",
        default=str(DEFAULT_ISOLATION_ROOT),
        help="Parent directory for isolated problem copies.",
    )
    parser.add_argument(
        "--keep-isolated-workspace",
        action="store_true",
        help="Do not remove the temporary isolated problem copy after syncing run artifacts.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without running preflight/claude/cleanup")
    args = parser.parse_args()

    source_problem_dir = Path(args.problem_dir).resolve()
    is_native = args.skill == "v2-native"
    if not is_native and not args.visual_variant:
        raise SystemExit("--visual-variant is required for v2 skill")
    if not is_native and requires_openrouter(args.visual_variant) and not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit(
            f"{args.visual_variant} requires OPENROUTER_API_KEY. "
            "Set it before launching this run, or use a native Claude visual variant."
        )
    if args.prompt and args.prompt_file:
        raise SystemExit("--prompt and --prompt-file are mutually exclusive")
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text()
    else:
        prompt = args.prompt or DEFAULT_PROMPT.replace("<run_id>", args.run_id)

    source_run_dir = source_problem_dir / "runs" / args.run_id
    planned_problem_dir = source_problem_dir if args.no_isolated_workspace else Path(args.isolation_root).expanduser() / "<isolated-copy>" / source_problem_dir.name
    planned_run_dir = planned_problem_dir / "runs" / args.run_id

    preflight_cmd = [
        sys.executable,
        str(PREFLIGHT),
        "--problem-dir",
        str(planned_problem_dir),
        "--skill",
        args.skill,
        "--harness",
        "claude",
        "--run-id",
        args.run_id,
    ]
    if is_native:
        pass  # No visual-setting or visual-variant for native
    else:
        preflight_cmd.extend(["--visual-setting", args.visual_setting])
        preflight_cmd.extend(["--visual-variant", args.visual_variant])
    if args.no_clean_before:
        preflight_cmd.append("--no-clean")

    claude_cmd = [
        args.claude_bin,
        "-p",
        "--output-format",
        "json",
        "--model",
        args.model,
        "--effort",
        args.reasoning_effort,
        "--permission-mode",
        args.permission_mode,
        "--no-session-persistence",
        prompt,
    ]

    if args.dry_run:
        cleanup_cmd = [sys.executable, str(PREFLIGHT), "--cleanup", "--problem-dir", str(planned_problem_dir)]
        print(json.dumps({
            "status": "dry_run",
            "source_problem_dir": str(source_problem_dir),
            "source_run_dir": str(source_run_dir),
            "isolated_workspace": not args.no_isolated_workspace,
            "planned_problem_dir": str(planned_problem_dir),
            "planned_run_dir": str(planned_run_dir),
            "preflight_cmd": preflight_cmd,
            "claude_cmd": claude_cmd,
            "harness_version": wrapper_version(args),
            "cleanup_cmd": None if args.keep_installed else cleanup_cmd,
        }, indent=2))
        return

    isolation_parent = None
    problem_dir = source_problem_dir
    if not args.no_isolated_workspace:
        isolation_parent, problem_dir = create_isolated_problem_copy(
            source_problem_dir,
            args.run_id,
            Path(args.isolation_root).expanduser(),
        )

    preflight_cmd[preflight_cmd.index(str(planned_problem_dir))] = str(problem_dir)
    preflight_result = run_json(preflight_cmd)
    run_dir = Path(preflight_result["manifest"]["run_dir"])
    run_dir.mkdir(parents=True, exist_ok=True)

    isolation_manifest = {
        "enabled": not args.no_isolated_workspace,
        "source_problem_dir": str(source_problem_dir),
        "source_run_dir": str(source_run_dir),
        "work_problem_dir": str(problem_dir),
        "work_run_dir": str(run_dir),
        "excluded_from_copy": sorted(["runs", "__pycache__", *ACTIVE_INSTALL_NAMES]),
        "keep_isolated_workspace": args.keep_isolated_workspace,
    }
    (run_dir / "isolation_manifest.json").write_text(json.dumps(isolation_manifest, indent=2) + "\n")
    (run_dir / "preflight_result.json").write_text(json.dumps(preflight_result, indent=2) + "\n")
    (run_dir / "claude_command.json").write_text(json.dumps({"cmd": claude_cmd}, indent=2) + "\n")
    (run_dir / "harness_version.json").write_text(json.dumps(wrapper_version(args), indent=2) + "\n")

    claude_result = subprocess.run(claude_cmd, cwd=problem_dir, capture_output=True, text=True)
    (run_dir / "claude_stdout.txt").write_text(claude_result.stdout)
    (run_dir / "claude_stderr.txt").write_text(claude_result.stderr)
    (run_dir / "claude_exit.json").write_text(json.dumps({"returncode": claude_result.returncode}, indent=2) + "\n")

    cleanup_result = None
    if not args.keep_installed:
        cleanup_result = cleanup(problem_dir, dry_run=False)
        (run_dir / "cleanup_result.json").write_text(json.dumps(cleanup_result, indent=2) + "\n")

    recovery_result = recover_misnamed_outputs(run_dir)
    output_check = verify_run_outputs(run_dir)
    (run_dir / "output_check.json").write_text(json.dumps(output_check, indent=2) + "\n")

    if not args.no_isolated_workspace:
        copy_run_artifacts(run_dir, source_run_dir)
        if isolation_parent is not None and not args.keep_isolated_workspace:
            shutil.rmtree(isolation_parent, ignore_errors=True)
        reported_run_dir = source_run_dir
    else:
        reported_run_dir = run_dir

    print(json.dumps({
        "status": "ok" if claude_result.returncode == 0 and output_check["ok"] else (
            "invalid_outputs" if claude_result.returncode == 0 else "claude_failed"
        ),
        "run_dir": str(reported_run_dir),
        "work_run_dir": str(run_dir),
        "isolated_workspace": not args.no_isolated_workspace,
        "claude_returncode": claude_result.returncode,
        "output_check": output_check,
        "output_recovery": recovery_result,
        "cleanup_ran": cleanup_result is not None,
    }, indent=2))
    raise SystemExit(claude_result.returncode if claude_result.returncode != 0 else (0 if output_check["ok"] else 2))


if __name__ == "__main__":
    main()
