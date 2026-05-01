#!/usr/bin/env python3
"""Run one Codex perception benchmark: preflight -> codex exec -> cleanup."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PREFLIGHT = SCRIPT_DIR / "preflight.py"


DEFAULT_PROMPT = """Run the current DexHoldem perception step.

Use the local setup and visible visual subagents. Do not execute robot actions.
Do not perform image perception in the main agent; merge subagent evidence only.

Write:
- runs/<run_id>/visual_raw/
- runs/<run_id>/visual_summary.json
- runs/<run_id>/eval_report.md
"""


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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path, base: Path) -> dict:
    return {
        "path": str(path.relative_to(base)),
        "sha256": file_sha256(path),
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


def default_host_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))


def prepare_run_codex_home(run_dir: Path, host_codex_home: Path) -> Path:
    codex_home = run_dir / ".codex_home"
    codex_home.mkdir(parents=True, exist_ok=True)

    auth_src = host_codex_home / "auth.json"
    if not auth_src.exists():
        raise RuntimeError(f"Codex auth file not found: {auth_src}")
    shutil.copy2(auth_src, codex_home / "auth.json")

    config = """model = "gpt-5.5"
service_tier = "fast"

[permissions.workspace_only.filesystem]
"/Users/ma-lab-hku/.ssh/**" = "none"
"/Users/ma-lab-hku/.codex/**" = "none"
"/Users/ma-lab-hku/**" = "none"
"""
    (codex_home / "config.toml").write_text(config)
    return codex_home


def verify_run_outputs(run_dir: Path) -> dict:
    visual_raw_dir = run_dir / "visual_raw"
    raw_files = sorted(path.relative_to(run_dir).as_posix() for path in visual_raw_dir.glob("*") if path.is_file())
    required = {
        "visual_summary": (run_dir / "visual_summary.json").exists(),
        "eval_report": (run_dir / "eval_report.md").exists(),
        "visual_raw_dir": visual_raw_dir.is_dir(),
        "visual_raw_files": bool(raw_files),
    }
    return {
        "ok": all(required.values()),
        "required": required,
        "visual_raw_files": raw_files,
    }


def wrapper_version(args: argparse.Namespace, codex_home: Path | None = None) -> dict:
    data = {
        "runner_script": file_record(Path(__file__).resolve(), SCRIPT_DIR.parent),
        "preflight_script": file_record(PREFLIGHT.resolve(), SCRIPT_DIR.parent),
        "codex_version": command_version([args.codex_bin, "--version"]),
        "python_version": command_version([sys.executable, "--version"]),
        "model": args.model,
        "model_reasoning_effort": args.reasoning_effort,
        "service_tier": args.service_tier,
        "sandbox": args.sandbox,
        "permission_profile": args.permission_profile,
    }
    if codex_home is not None:
        config = codex_home / "config.toml"
        if config.exists():
            data["run_codex_home_config"] = file_record(config, codex_home)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem-dir", required=True, help="Problem folder, e.g. bench/problems/p3")
    parser.add_argument("--visual-setting", choices=("general", "split"), default="split")
    parser.add_argument("--visual-variant", required=True, help="Variant under subagent/, e.g. codex_native_gpt5_4_mini_medium")
    parser.add_argument("--run-id", required=True, help="Run folder name under problem_dir/runs/")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--service-tier", default="fast")
    parser.add_argument("--sandbox", default="workspace-write", choices=("read-only", "workspace-write", "danger-full-access"))
    parser.add_argument("--prompt", help="Inline prompt for codex exec. Defaults to the benchmark prompt.")
    parser.add_argument("--prompt-file", help="Read codex exec prompt from this file.")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument(
        "--host-codex-home",
        default=str(default_host_codex_home()),
        help="Host Codex home used only by the wrapper to copy auth.json into the run-local CODEX_HOME.",
    )
    parser.add_argument("--permission-profile", default="workspace_only", help="Codex default_permissions profile to use")
    parser.add_argument(
        "--ignore-user-config",
        action="store_true",
        help="Do not load ~/.codex/config.toml. This disables --permission-profile unless the same profile is supplied by other config.",
    )
    parser.add_argument(
        "--persist-session",
        action="store_true",
        help="Allow Codex to persist session files. Default is --ephemeral.",
    )
    parser.add_argument("--keep-installed", action="store_true", help="Do not cleanup active install after codex exits")
    parser.add_argument("--no-clean-before", action="store_true", help="Do not ask preflight to clean previous install first")
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without running preflight/codex/cleanup")
    args = parser.parse_args()

    problem_dir = Path(args.problem_dir).resolve()
    if args.prompt and args.prompt_file:
        raise SystemExit("--prompt and --prompt-file are mutually exclusive")
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text()
    else:
        prompt = args.prompt or DEFAULT_PROMPT.replace("<run_id>", args.run_id)
    planned_run_dir = problem_dir / "runs" / args.run_id

    preflight_cmd = [
        sys.executable,
        str(PREFLIGHT),
        "--problem-dir",
        str(problem_dir),
        "--visual-setting",
        args.visual_setting,
        "--visual-variant",
        args.visual_variant,
        "--run-id",
        args.run_id,
    ]
    if args.no_clean_before:
        preflight_cmd.append("--no-clean")

    codex_cmd = [
        args.codex_bin,
        "exec",
        "-C",
        str(problem_dir),
        "-s",
        args.sandbox,
        "-m",
        args.model,
        "-c",
        f"model_reasoning_effort={args.reasoning_effort}",
        "-c",
        f"service_tier={args.service_tier}",
        "-c",
        f'default_permissions="{args.permission_profile}"',
        "-c",
        f'permissions.{args.permission_profile}.filesystem."{problem_dir}"="read"',
        "-c",
        f'permissions.{args.permission_profile}.filesystem."{problem_dir}/**"="read"',
        "-c",
        f'permissions.{args.permission_profile}.filesystem."{planned_run_dir}"="write"',
        "-c",
        f'permissions.{args.permission_profile}.filesystem."{planned_run_dir}/**"="write"',
        "-c",
        "sandbox_permissions=[]",
        "-c",
        "shell_environment_policy.inherit=none",
        prompt,
    ]
    if args.ignore_user_config:
        codex_cmd.insert(2, "--ignore-user-config")
    if not args.persist_session:
        codex_cmd.insert(2, "--ephemeral")

    if args.dry_run:
        planned_codex_home = planned_run_dir / ".codex_home"
        cleanup_cmd = [sys.executable, str(PREFLIGHT), "--cleanup", "--problem-dir", str(problem_dir)]
        print(json.dumps({
            "status": "dry_run",
            "preflight_cmd": preflight_cmd,
            "codex_cmd": codex_cmd,
            "codex_env": {"CODEX_HOME": str(planned_codex_home)},
            "harness_version": wrapper_version(args),
            "host_auth_source": str(Path(args.host_codex_home).expanduser() / "auth.json"),
            "cleanup_cmd": None if args.keep_installed else cleanup_cmd,
        }, indent=2))
        return

    preflight_result = run_json(preflight_cmd)
    run_dir = Path(preflight_result["manifest"]["run_dir"])
    run_dir.mkdir(parents=True, exist_ok=True)
    codex_home = prepare_run_codex_home(run_dir, Path(args.host_codex_home).expanduser())
    (run_dir / "preflight_result.json").write_text(json.dumps(preflight_result, indent=2) + "\n")
    (run_dir / "codex_command.json").write_text(json.dumps({"cmd": codex_cmd}, indent=2) + "\n")
    (run_dir / "codex_env.json").write_text(json.dumps({"CODEX_HOME": str(codex_home)}, indent=2) + "\n")
    (run_dir / "harness_version.json").write_text(json.dumps(wrapper_version(args, codex_home), indent=2) + "\n")

    codex_env = os.environ.copy()
    codex_env["CODEX_HOME"] = str(codex_home)
    codex_result = subprocess.run(codex_cmd, cwd=problem_dir, capture_output=True, text=True, env=codex_env)
    (run_dir / "codex_stdout.txt").write_text(codex_result.stdout)
    (run_dir / "codex_stderr.txt").write_text(codex_result.stderr)
    (run_dir / "codex_exit.json").write_text(json.dumps({"returncode": codex_result.returncode}, indent=2) + "\n")
    shutil.rmtree(codex_home, ignore_errors=True)

    cleanup_result = None
    if not args.keep_installed:
        cleanup_result = cleanup(problem_dir, dry_run=False)
        (run_dir / "cleanup_result.json").write_text(json.dumps(cleanup_result, indent=2) + "\n")

    output_check = verify_run_outputs(run_dir)
    (run_dir / "output_check.json").write_text(json.dumps(output_check, indent=2) + "\n")

    print(json.dumps({
        "status": "ok" if codex_result.returncode == 0 and output_check["ok"] else (
            "invalid_outputs" if codex_result.returncode == 0 else "codex_failed"
        ),
        "run_dir": str(run_dir),
        "codex_returncode": codex_result.returncode,
        "output_check": output_check,
        "cleanup_ran": cleanup_result is not None,
    }, indent=2))
    raise SystemExit(codex_result.returncode if codex_result.returncode != 0 else (0 if output_check["ok"] else 2))


if __name__ == "__main__":
    main()
