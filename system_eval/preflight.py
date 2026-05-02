#!/usr/bin/env python3
"""Create a real DexHoldem system-eval experiment workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_SOURCE = ROOT / "skills" / "dexholdem-v2"
SUBAGENT_ROOT = ROOT / "subagent"
DEFAULT_EXPERIMENTS_ROOT = ROOT / "experiments"
DEFAULT_CODEX_VARIANT = "codex_native_gpt5_4_mini_medium"
DEFAULT_CLAUDE_VARIANT = "claude_sonnet_4_6_medium"
RUNTIME_FILES = (
    "utils.py",
    "capture.py",
    "state.py",
    "executor.py",
    "action_translator.py",
    "text_to_sound.py",
    "router.py",
    "remote_exec.py",
)


def default_hole_cache() -> dict:
    return {
        "schema_version": 1,
        "left": {"card": None, "status": "unknown", "source_state": None, "confidence": 0.0},
        "right": {"card": None, "status": "unknown", "source_state": None, "confidence": 0.0},
        "blinds": {
            "dealer": None,
            "small_blind": None,
            "big_blind": None,
            "source_state": None,
            "status": "unknown",
        },
    }


def default_action_sequence() -> dict:
    return {
        "schema_version": 1,
        "sequence_id": None,
        "loop_stage": "idle",
        "intent": None,
        "action": None,
        "plan": None,
        "steps": [],
        "current_step": None,
        "retry_count": 0,
        "last_error": None,
        "human_required": False,
        "safety_counters": {
            "consecutive_waits": 0,
            "total_waits": 0,
            "consecutive_recoveries": 0,
            "total_recoveries": 0,
            "executor_failures": 0,
            "action_sequences_started": 0,
        },
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def copytree_clean(src: Path, dest: Path) -> None:
    if dest.exists() or dest.is_symlink():
        remove_path(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", ".venv"))


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def replace_symlink(link: Path, target: Path | str) -> None:
    if link.exists() or link.is_symlink():
        remove_path(link)
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target)


def relative_target(link: Path, target: Path) -> Path:
    return Path(os.path.relpath(target, start=link.parent))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path, base: Path = ROOT) -> dict:
    return {
        "path": str(path.relative_to(base)),
        "sha256": file_sha256(path),
        "size": path.stat().st_size,
    }


def tree_records(path: Path, base: Path = ROOT) -> list[dict]:
    return [
        file_record(item, base)
        for item in sorted(path.rglob("*"))
        if item.is_file() and item.name not in {".DS_Store"} and "__pycache__" not in item.parts
    ]


def validate_exp_name(name: str) -> None:
    if not name or name in {".", ".."}:
        raise SystemExit("--exp-name must be a non-empty directory name")
    if Path(name).name != name:
        raise SystemExit("--exp-name must be a single directory name, not a path")


def split_agent_files(variant: str, suffix: str) -> list[Path]:
    split_dir = SUBAGENT_ROOT / variant / "split"
    if not split_dir.exists():
        raise SystemExit(f"split subagent directory does not exist: {split_dir}")
    files = sorted(split_dir.glob(f"*{suffix}"))
    if not files:
        raise SystemExit(f"no split subagents found under: {split_dir}")
    return files


def install_agent_files(files: list[Path], target_dir: Path) -> list[dict]:
    target_dir.mkdir(parents=True, exist_ok=True)
    installed = []
    for src in files:
        dest = target_dir / src.name
        shutil.copy2(src, dest)
        installed.append({"name": src.stem, "source": str(src.relative_to(ROOT)), "path": str(dest)})
    return installed


def install_skill(exp_dir: Path) -> dict:
    shared_skill = exp_dir / ".agent" / "skills" / "dexholdem-v2"
    copytree_clean(SKILL_SOURCE, shared_skill)

    links = {}
    for link in (
        exp_dir / ".claude" / "skills" / "dexholdem-v2",
        exp_dir / ".codex" / "skills" / "dexholdem-v2",
    ):
        replace_symlink(link, relative_target(link, shared_skill))
        links[str(link.relative_to(exp_dir))] = os.readlink(link)

    agents_link = exp_dir / ".agents"
    replace_symlink(agents_link, ".agent")
    links[str(agents_link.relative_to(exp_dir))] = os.readlink(agents_link)

    return {"shared_skill": str(shared_skill), "links": links}


def expose_runtime(exp_dir: Path) -> dict:
    skill_dir = exp_dir / ".agent" / "skills" / "dexholdem-v2"
    exposed = []
    for name in RUNTIME_FILES:
        link = exp_dir / name
        target = skill_dir / "scripts" / name
        replace_symlink(link, relative_target(link, target))
        exposed.append(str(link.relative_to(exp_dir)))

    for name in ("config.yaml", "pyproject.toml"):
        shutil.copy2(skill_dir / name, exp_dir / name)
        exposed.append(name)

    visual_link = exp_dir / "visual_guidelines"
    replace_symlink(visual_link, relative_target(visual_link, skill_dir / "visual_guidelines"))
    exposed.append(str(visual_link.relative_to(exp_dir)))

    return {"runtime_entries": exposed}


def run_uv_sync(exp_dir: Path) -> dict:
    skill_dir = exp_dir / ".agent" / "skills" / "dexholdem-v2"
    if shutil.which("uv") is None:
        raise SystemExit("uv not found on PATH; install uv or omit --uv-sync")
    result = subprocess.run(["uv", "sync"], cwd=skill_dir, capture_output=True, text=True, timeout=300)
    detail = {
        "command": ["uv", "sync"],
        "cwd": str(skill_dir),
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-1000:],
        "stderr_tail": result.stderr[-1000:],
    }
    if result.returncode != 0:
        raise SystemExit(json.dumps({"status": "failed", "step": "uv_sync", "detail": detail}, indent=2))
    return detail


def init_state(exp_dir: Path) -> dict:
    (exp_dir / "s0").mkdir(parents=True, exist_ok=True)
    replace_symlink(exp_dir / "s_current", "s0")
    (exp_dir / "hole_card_cache.json").write_text(json.dumps(default_hole_cache(), indent=2) + "\n")
    (exp_dir / "action_sequence.json").write_text(json.dumps(default_action_sequence(), indent=2) + "\n")
    return {
        "state": "s0",
        "state_dir": str(exp_dir / "s0"),
        "current": os.readlink(exp_dir / "s_current"),
    }


def capture_initial(exp_dir: Path, source: str | None = None) -> dict:
    output = exp_dir / "s0" / "00_capture.jpg"
    if source:
        source_path = Path(source)
        if not source_path.is_absolute():
            source_path = (ROOT / source_path).resolve()
        if not source_path.exists():
            raise SystemExit(f"camera source does not exist: {source_path}")
        shutil.copy2(source_path, output)
        return {"mode": "source_copy", "source": str(source_path), "output": str(output)}

    venv_python = exp_dir / ".agent" / "skills" / "dexholdem-v2" / ".venv" / "bin" / "python"
    python = str(venv_python) if venv_python.exists() else sys.executable
    command = [python, str(exp_dir / "capture.py"), "--output", str(output), "--meta"]
    result = subprocess.run(command, cwd=exp_dir, capture_output=True, text=True, timeout=30)
    detail = {
        "command": command,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-1000:],
        "stderr_tail": result.stderr[-1000:],
        "output": str(output),
    }
    if result.returncode != 0:
        raise SystemExit(json.dumps({"status": "failed", "step": "capture_initial", "detail": detail}, indent=2))
    return detail


def model_checks(codex_files: list[Path], claude_files: list[Path]) -> list[dict]:
    checks = []
    for path in codex_files:
        text = path.read_text()
        checks.append({
            "path": str(path.relative_to(ROOT)),
            "expected": {"model": "gpt-5.4-mini", "model_reasoning_effort": "medium"},
            "ok": 'model = "gpt-5.4-mini"' in text and 'model_reasoning_effort = "medium"' in text,
        })
    for path in claude_files:
        text = path.read_text()
        checks.append({
            "path": str(path.relative_to(ROOT)),
            "expected": {"model": "claude-sonnet-4-6", "effort": "medium"},
            "ok": "model: claude-sonnet-4-6" in text and "effort: medium" in text,
        })
    return checks


def build_manifest(args: argparse.Namespace, exp_dir: Path, codex_files: list[Path], claude_files: list[Path]) -> dict:
    return {
        "schema_version": 1,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": {
            "name": args.exp_name,
            "root": str(exp_dir),
            "current_link": str(exp_dir.parent / "current"),
        },
        "defaults": {
            "visual_setting": "split",
            "codex_variant": args.codex_variant,
            "claude_variant": args.claude_variant,
        },
        "source": {
            "skill": str(SKILL_SOURCE.relative_to(ROOT)),
            "codex_subagents": [file_record(path) for path in codex_files],
            "claude_subagents": [file_record(path) for path in claude_files],
            "skill_files": tree_records(SKILL_SOURCE),
        },
        "model_checks": model_checks(codex_files, claude_files),
    }


def create_experiment(args: argparse.Namespace) -> dict:
    validate_exp_name(args.exp_name)
    experiments_root = Path(args.experiments_root).resolve()
    exp_dir = experiments_root / args.exp_name
    codex_files = split_agent_files(args.codex_variant, ".toml")
    claude_files = split_agent_files(args.claude_variant, ".md")

    manifest = build_manifest(args, exp_dir, codex_files, claude_files)
    if args.dry_run:
        manifest["dry_run"] = True
        return {"status": "dry_run", "manifest": manifest}

    if exp_dir.exists() and not args.force:
        raise SystemExit(f"experiment already exists: {exp_dir} (pass --force to replace it)")
    if exp_dir.exists():
        remove_path(exp_dir)

    exp_dir.mkdir(parents=True)
    skill_result = install_skill(exp_dir)
    runtime_result = expose_runtime(exp_dir)
    uv_result = run_uv_sync(exp_dir) if args.uv_sync else {"skipped": True}
    state_result = init_state(exp_dir)
    capture_result = capture_initial(exp_dir, args.camera_source) if args.capture_initial else {"skipped": True}

    codex_installed = install_agent_files(codex_files, exp_dir / ".codex" / "agents")
    claude_installed = install_agent_files(claude_files, exp_dir / ".claude" / "agents")

    if not args.no_current:
        replace_symlink(exp_dir.parent / "current", exp_dir)

    manifest.update({
        "installed": {
            "skill": skill_result,
            "runtime": runtime_result,
            "uv_sync": uv_result,
            "state": state_result,
            "capture": capture_result,
            "codex_agents": codex_installed,
            "claude_agents": claude_installed,
        }
    })
    (exp_dir / "system_eval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    return {"status": "ok", "experiment": str(exp_dir), "manifest": manifest}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp-name", required=True, help="Experiment directory name to create")
    parser.add_argument("--experiments-root", default=str(DEFAULT_EXPERIMENTS_ROOT))
    parser.add_argument("--codex-variant", default=DEFAULT_CODEX_VARIANT)
    parser.add_argument("--claude-variant", default=DEFAULT_CLAUDE_VARIANT)
    parser.add_argument("--force", action="store_true", help="Replace an existing experiment directory")
    parser.add_argument("--dry-run", action="store_true", help="Print the planned setup without writing files")
    parser.add_argument("--no-current", action="store_true", help="Do not update experiments/current")
    parser.add_argument("--capture-initial", action="store_true", help="Capture s0/00_capture.jpg after setup")
    parser.add_argument("--camera-source", help="With --capture-initial, copy an existing image as s0/00_capture.jpg")
    parser.add_argument("--uv-sync", action="store_true", help="Run uv sync in the copied dexholdem-v2 skill")
    args = parser.parse_args()

    print(json.dumps(create_experiment(args), indent=2))


if __name__ == "__main__":
    main()
