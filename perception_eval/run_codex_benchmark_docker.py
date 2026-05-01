#!/usr/bin/env python3
"""Run one Codex perception benchmark inside a minimal Docker container."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PREFLIGHT = SCRIPT_DIR / "preflight.py"
DOCKERFILE = SCRIPT_DIR / "Dockerfile.codex"


DEFAULT_PROMPT = """You are the main Codex benchmark harness agent for this DexHoldem perception problem.

Work only inside the current problem folder. Use the visible visual agents as
read-only evidence providers and the visible reasoning agent for Texas Hold'em
action reasoning. Do not execute robot actions. Do not modify ground-truth
files outside this folder.

Do not read files outside the current problem folder. Treat the current problem
folder as the complete workspace.

Inspect the latest state pointed to by s_current, use the available visual
agents according to the installed setting, and merge their evidence into:

- runs/<run_id>/visual_summary.json
- runs/<run_id>/eval_report.md

The final visual_summary.json label must include blind info and, when required
by the problem setting, winning-condition judgment. Preserve uncertainty rather
than guessing.
"""


def run_json(cmd: list[str], *, cwd: Path | None = None) -> dict:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {shlex.join(cmd)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return json.loads(result.stdout)


def run_checked(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {shlex.join(cmd)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def cleanup(problem_dir: Path) -> dict:
    return run_json([sys.executable, str(PREFLIGHT), "--cleanup", "--problem-dir", str(problem_dir)])


def default_codex_auth() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem-dir", required=True, help="Problem folder, e.g. bench/problems/p3")
    parser.add_argument("--visual-setting", choices=("general", "split"), default="split")
    parser.add_argument("--visual-variant", required=True, help="Variant under subagent/")
    parser.add_argument("--run-id", required=True, help="Run folder name under problem_dir/runs/")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--service-tier", default="fast")
    parser.add_argument("--sandbox", default="workspace-write", choices=("read-only", "workspace-write", "danger-full-access"))
    parser.add_argument("--prompt", help="Inline prompt for codex exec. Defaults to the benchmark prompt.")
    parser.add_argument("--prompt-file", help="Read codex exec prompt from this file.")
    parser.add_argument("--image", default="dexholdem-codex-cli:0.125.0")
    parser.add_argument("--build-image", action="store_true", help="Build the minimal Codex image before running")
    parser.add_argument("--codex-cli-version", default="0.125.0")
    parser.add_argument("--auth-json", default=str(default_codex_auth()), help="Host Codex auth.json to mount read-only")
    parser.add_argument("--docker-bin", default="docker")
    parser.add_argument("--keep-installed", action="store_true", help="Do not cleanup active install after Codex exits")
    parser.add_argument("--no-clean-before", action="store_true", help="Do not ask preflight to clean previous install first")
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without running Docker")
    args = parser.parse_args()

    problem_dir = Path(args.problem_dir).resolve()
    auth_json = Path(args.auth_json).expanduser().resolve()
    if args.prompt and args.prompt_file:
        raise SystemExit("--prompt and --prompt-file are mutually exclusive")
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text()
    else:
        prompt = (args.prompt or DEFAULT_PROMPT).replace("<run_id>", args.run_id)

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

    build_cmd = [
        args.docker_bin,
        "build",
        "-f",
        str(DOCKERFILE),
        "--build-arg",
        f"CODEX_CLI_VERSION={args.codex_cli_version}",
        "-t",
        args.image,
        str(SCRIPT_DIR),
    ]

    codex_args = [
        "codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "-C",
        "/workspace",
        "-s",
        args.sandbox,
        "-m",
        args.model,
        "-c",
        f"model_reasoning_effort={args.reasoning_effort}",
        "-c",
        f"service_tier={args.service_tier}",
        "-c",
        "sandbox_permissions=[]",
        "-c",
        "shell_environment_policy.inherit=none",
        prompt,
    ]
    container_script = (
        "set -eu; "
        "mkdir -p /tmp/codex-home; "
        "cp /codex-auth/auth.json /tmp/codex-home/auth.json; "
        "export CODEX_HOME=/tmp/codex-home; "
        f"{shlex.join(codex_args)}"
    )

    docker_cmd = [
        args.docker_bin,
        "run",
        "--rm",
        "--mount",
        f"type=bind,src={problem_dir},dst=/workspace",
        "--mount",
        f"type=bind,src={auth_json},dst=/codex-auth/auth.json,readonly",
        "-w",
        "/workspace",
        args.image,
        "sh",
        "-lc",
        container_script,
    ]

    if args.dry_run:
        print(json.dumps({
            "status": "dry_run",
            "preflight_cmd": preflight_cmd,
            "build_cmd": build_cmd if args.build_image else None,
            "docker_cmd": docker_cmd,
            "cleanup_cmd": None if args.keep_installed else [
                sys.executable,
                str(PREFLIGHT),
                "--cleanup",
                "--problem-dir",
                str(problem_dir),
            ],
            "mounted_paths": {
                "workspace_rw": str(problem_dir),
                "codex_auth_ro": str(auth_json),
            },
        }, indent=2))
        return

    if not auth_json.exists():
        raise SystemExit(f"Codex auth file does not exist: {auth_json}")

    preflight_result = run_json(preflight_cmd)
    run_dir = Path(preflight_result["manifest"]["run_dir"])
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "preflight_result.json").write_text(json.dumps(preflight_result, indent=2) + "\n")

    if args.build_image:
        build_result = run_checked(build_cmd)
        (run_dir / "docker_build_stdout.txt").write_text(build_result.stdout)
        (run_dir / "docker_build_stderr.txt").write_text(build_result.stderr)

    (run_dir / "docker_command.json").write_text(json.dumps({"cmd": docker_cmd}, indent=2) + "\n")
    codex_result = subprocess.run(docker_cmd, capture_output=True, text=True)
    (run_dir / "codex_stdout.txt").write_text(codex_result.stdout)
    (run_dir / "codex_stderr.txt").write_text(codex_result.stderr)
    (run_dir / "codex_exit.json").write_text(json.dumps({"returncode": codex_result.returncode}, indent=2) + "\n")

    cleanup_result = None
    if not args.keep_installed:
        cleanup_result = cleanup(problem_dir)
        (run_dir / "cleanup_result.json").write_text(json.dumps(cleanup_result, indent=2) + "\n")

    print(json.dumps({
        "status": "ok" if codex_result.returncode == 0 else "codex_failed",
        "run_dir": str(run_dir),
        "codex_returncode": codex_result.returncode,
        "cleanup_ran": cleanup_result is not None,
    }, indent=2))
    raise SystemExit(codex_result.returncode)


if __name__ == "__main__":
    main()
