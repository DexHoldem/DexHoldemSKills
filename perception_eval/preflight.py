#!/usr/bin/env python3
"""Perception-eval preflight for one benchmark problem and one agent setting."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "subagent"
SKILLS_ROOT = ROOT / "skills"
CODEX_AGENT_DIR = ".codex/agents"
CLAUDE_AGENT_DIR = ".claude/agents"

SUPPORTED_SKILLS = ("v2", "v2-native")

ACTIVE_FILES = (
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
    # Keep this cleanup entry so stale installs from older harness versions are
    # removed, but do not install PERCEPTION_CONTEXT.md for new runs.
    "PERCEPTION_CONTEXT.md",
)

ACTIVE_DIRS = (
    "visual_guidelines",
)


GENERAL_PROMPT = """# General Visual-Agent Setup

Use the single visible visual agent for image perception.

The main agent must not inspect images or independently decide visual fields.
Delegate image-reading questions to the visual agent and merge only its
returned evidence.
Do not run helper scripts, call a reasoning agent, or choose a poker action.

Write raw evidence to `runs/<run_id>/visual_raw/visual_agent.md`.

Then write `runs/<run_id>/visual_summary.json` and
`runs/<run_id>/eval_report.md`. Do not execute robot actions.
"""


SPLIT_PROMPT = """# Split Visual-Agent Setup

Use the visible split visual agents for image perception.

The main agent must not inspect images or independently decide visual fields.
Delegate each image-reading question to the appropriate scoped visual agent and
merge only returned evidence.
Do not run helper scripts, call a reasoning agent, or choose a poker action.
Run independent visual subagents in parallel whenever possible. If the runtime
agent limit prevents full parallelism, run them in waves; do not serialize them
unless a dependency or limit requires it.

Write one raw evidence file per called subagent under
`runs/<run_id>/visual_raw/<agent_name>.md`.

Then write `runs/<run_id>/visual_summary.json` and
`runs/<run_id>/eval_report.md`. Do not execute robot actions.
"""


NATIVE_PROMPT = """# Native Perception Setup

Perform visual perception directly without delegating to subagents.

Read the capture image and extract all visual fields following the guidelines
in `visual_guidelines/`. Do not run helper scripts, call a reasoning agent,
or choose a poker action.

Write your raw perception evidence to `runs/<run_id>/visual_raw/native.md`.

Then write `runs/<run_id>/visual_summary.json` and
`runs/<run_id>/eval_report.md`. Do not execute robot actions.
"""


def infer_harness(variant: str) -> str | None:
    if variant.startswith("codex"):
        return "codex"
    if variant.startswith("claude"):
        return "claude"
    return None


def copytree_clean(src: Path, dest: Path) -> None:
    if dest.exists() or dest.is_symlink():
        if dest.is_symlink() or dest.is_file():
            dest.unlink()
        else:
            shutil.rmtree(dest)
    shutil.copytree(src, dest)


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


def tree_records(root: Path, base: Path) -> list[dict]:
    if not root.exists():
        return []
    return [file_record(path, base) for path in sorted(root.rglob("*")) if path.is_file()]


def remove_path(path: Path, *, dry_run: bool) -> bool:
    if not path.exists() and not path.is_symlink():
        return False
    if dry_run:
        return True
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    return True


def clean_nested_agent_dir(problem_dir: Path, relative_dir: str, parent_name: str, *, dry_run: bool) -> list[str]:
    removed = []
    agents_dir = problem_dir / relative_dir
    if remove_path(agents_dir, dry_run=dry_run):
        removed.append(str(agents_dir))

    parent_dir = problem_dir / parent_name
    if parent_dir.exists() and parent_dir.is_dir():
        try:
            is_empty = not any(parent_dir.iterdir())
        except OSError:
            is_empty = False
        if is_empty:
            removed.append(str(parent_dir))
            if not dry_run:
                parent_dir.rmdir()
    return removed


def clean_problem(problem_dir: Path, *, remove_runs: bool, dry_run: bool) -> dict:
    removed = []
    preserved = []

    for name in ACTIVE_FILES:
        path = problem_dir / name
        if remove_path(path, dry_run=dry_run):
            removed.append(str(path))

    for name in ACTIVE_DIRS:
        path = problem_dir / name
        if remove_path(path, dry_run=dry_run):
            removed.append(str(path))

    removed.extend(clean_nested_agent_dir(problem_dir, CODEX_AGENT_DIR, ".codex", dry_run=dry_run))
    removed.extend(clean_nested_agent_dir(problem_dir, CLAUDE_AGENT_DIR, ".claude", dry_run=dry_run))

    runs_dir = problem_dir / "runs"
    if remove_runs:
        if remove_path(runs_dir, dry_run=dry_run):
            removed.append(str(runs_dir))
    elif runs_dir.exists():
        preserved.append(str(runs_dir))

    for name in ("hole_card_cache.json", "action_sequence.json", "s_current"):
        path = problem_dir / name
        if path.exists() or path.is_symlink():
            preserved.append(str(path))
    preserved.extend(str(path) for path in sorted(problem_dir.glob("s[0-9]*")) if path.is_dir())

    return {"removed": removed, "preserved": preserved}


def list_variants() -> dict:
    variants = []
    for source_dir in sorted(path for path in SOURCE_ROOT.iterdir() if path.is_dir()):
        harness = infer_harness(source_dir.name)
        if harness is None:
            continue
        available_settings = []
        if agent_source_files(source_dir, harness, "general"):
            available_settings.append("general")
        if agent_source_files(source_dir, harness, "split"):
            available_settings.append("split")
        variants.append({
            "visual_variant": source_dir.name,
            "harness": harness,
            "available_settings": available_settings,
        })
    return {"schema_version": 1, "variants": variants}


def agent_source_files(source_dir: Path, harness: str, setting: str) -> list[Path]:
    if setting == "general":
        filename = "visual_agent.toml" if harness == "codex" else "visual-agent.md"
        path = source_dir / filename
        return [path] if path.exists() else []

    pattern = "*.toml" if harness == "codex" else "*.md"
    split_dir = source_dir / "split"
    return sorted(split_dir.glob(pattern)) if split_dir.exists() else []


def unique_paths(paths: list[Path]) -> list[Path]:
    seen = set()
    result = []
    for path in paths:
        key = path.resolve()
        if key in seen:
            continue
        seen.add(key)
        result.append(path)
    return result


def latest_state(problem_dir: Path) -> str | None:
    link = problem_dir / "s_current"
    if link.exists():
        return link.resolve().name

    states = []
    for path in problem_dir.iterdir():
        if not path.is_dir() or not path.name.startswith("s"):
            continue
        suffix = path.name[1:]
        if suffix.isdigit():
            states.append((int(suffix), path.name))
    return sorted(states)[-1][1] if states else None


def default_run_id(problem_dir: Path, harness: str, setting: str, variant: str) -> str:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    return f"{problem_dir.name}_{harness}_{setting}_{variant}_{stamp}"


def skill_root(skill: str) -> Path:
    if skill == "v2":
        return SKILLS_ROOT / "dexholdem-v2"
    elif skill == "v2-native":
        return SKILLS_ROOT / "dexholdem-v2-native"
    raise ValueError(f"unsupported skill: {skill}")


def copy_visual_context(problem_dir: Path, skill: str) -> list[str]:
    copied = []
    src = skill_root(skill) / "visual_guidelines"
    copytree_clean(src, problem_dir / "visual_guidelines")
    copied.append("visual_guidelines/")
    return copied


def install_agents(problem_dir: Path, source_files: list[Path], harness: str) -> tuple[str, list[str]]:
    if harness == "codex":
        target = problem_dir / CODEX_AGENT_DIR
    elif harness == "claude":
        target = problem_dir / CLAUDE_AGENT_DIR
    else:
        raise RuntimeError(f"unsupported harness: {harness}")

    if target.exists() or target.is_symlink():
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    visible_agents = []
    for src in source_files:
        shutil.copy2(src, target / src.name)
        visible_agents.append(src.stem)
    return str(target.relative_to(problem_dir)), visible_agents


def validate_problem(problem_dir: Path, state: str | None) -> list[str]:
    warnings = []
    if state is None:
        warnings.append("no sN state folders found")
    else:
        capture = problem_dir / state / "00_capture.jpg"
        if not capture.exists():
            warnings.append(f"latest state capture missing: {capture.relative_to(problem_dir)}")

    for cache_name in ("hole_card_cache.json", "action_sequence.json"):
        if not (problem_dir / cache_name).exists():
            warnings.append(f"cache missing: {cache_name}")
    return warnings


def install(args: argparse.Namespace) -> dict:
    problem_dir = Path(args.problem_dir).resolve()
    if not problem_dir.exists():
        raise SystemExit(f"problem dir does not exist: {problem_dir}")
    if not problem_dir.is_dir():
        raise SystemExit(f"problem dir is not a directory: {problem_dir}")

    skill = args.skill
    is_native = skill == "v2-native"
    sk_root = skill_root(skill)

    if is_native:
        # Native mode: no subagents, harness does perception directly
        if not args.harness:
            raise SystemExit("--harness is required for v2-native skill")
        harness = args.harness
        variant = None
        source_files = []
        visual_source_files = []
    else:
        # v2 mode: use subagents
        variant = args.visual_variant
        if not variant:
            raise SystemExit("--visual-variant is required for v2 skill")
        source_dir = SOURCE_ROOT / variant
        if not source_dir.exists():
            raise SystemExit(f"visual variant does not exist: {source_dir}")

        inferred = infer_harness(variant)
        harness = args.harness or inferred
        if harness is None:
            raise SystemExit(f"could not infer harness from variant name: {variant}")
        if inferred and args.harness and args.harness != inferred:
            raise SystemExit(f"harness {args.harness!r} does not match variant {variant!r}, inferred {inferred!r}")

        visual_source_files = agent_source_files(source_dir, harness, args.visual_setting)
        if not visual_source_files:
            raise SystemExit(
                f"variant {variant!r} does not provide {args.visual_setting!r} agents for harness {harness!r}"
            )
        source_files = unique_paths(visual_source_files)

    if args.clean_first:
        clean_result = clean_problem(problem_dir, remove_runs=False, dry_run=args.dry_run)
    else:
        clean_result = {"removed": [], "preserved": []}

    state = latest_state(problem_dir)
    if is_native:
        run_id = args.run_id or f"{problem_dir.name}_{harness}_native_{time.strftime('%Y%m%d_%H%M%S')}"
    else:
        run_id = args.run_id or default_run_id(problem_dir, harness, args.visual_setting, variant)
    run_dir = problem_dir / "runs" / run_id

    manifest = {
        "schema_version": 1,
        "skill": skill,
        "harness": harness,
        "visual_setting": "native" if is_native else args.visual_setting,
        "visual_variant": variant,
        "source_dir": None if is_native else str((SOURCE_ROOT / variant).relative_to(ROOT)),
        "problem_dir": str(problem_dir),
        "run_id": run_id,
        "run_dir": str(run_dir),
        "latest_state": state,
    }

    if args.dry_run:
        if is_native:
            visible_agent_dir = None
            visible_agents = []
        else:
            visible_agent_dir = CODEX_AGENT_DIR if harness == "codex" else CLAUDE_AGENT_DIR
            visible_agents = [path.stem for path in source_files]
        copied_runtime = []
    else:
        if is_native:
            visible_agent_dir = None
            visible_agents = []
        else:
            visible_agent_dir, visible_agents = install_agents(problem_dir, source_files, harness)
        copied_runtime = copy_visual_context(problem_dir, skill)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "visual_raw").mkdir(exist_ok=True)
        if is_native:
            prompt = NATIVE_PROMPT
        elif args.visual_setting == "general":
            prompt = GENERAL_PROMPT
        else:
            prompt = SPLIT_PROMPT
        (run_dir / "harness_prompt.md").write_text(prompt)

    manifest.update({
        "visible_agent_dir": visible_agent_dir,
        "visible_agents": visible_agents,
        "version": {
            "preflight_script": file_record(Path(__file__).resolve(), ROOT),
            "skill_root": str(sk_root.relative_to(ROOT)),
            "source_agents": [file_record(path, ROOT) for path in source_files],
            "visual_source_agents": [file_record(path, ROOT) for path in visual_source_files],
            "visual_guidelines": tree_records(sk_root / "visual_guidelines", ROOT),
        },
    })

    warnings = validate_problem(problem_dir, state)
    if not args.dry_run:
        (run_dir / "agent_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    if args.strict and warnings:
        raise SystemExit("\n".join(warnings))

    return {
        "status": "dry_run" if args.dry_run else ("ok" if not warnings else "ok_with_warnings"),
        "manifest": manifest,
        "clean": clean_result,
        "copied_runtime": copied_runtime,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List available source variants and exit")
    parser.add_argument("--cleanup", action="store_true", help="Clean active install artifacts from --problem-dir")
    parser.add_argument("--problem-dir", help="Problem folder, e.g. bench/problems/p3")
    parser.add_argument("--skill", choices=SUPPORTED_SKILLS, default="v2", help="Skill to use: v2 (subagents) or v2-native (no subagents)")
    parser.add_argument("--harness", choices=("codex", "claude"), help="Harness type; inferred from variant by default for v2, required for v2-native")
    parser.add_argument("--visual-setting", choices=("general", "split"), default="split", help="Visual agent setting (v2 only)")
    parser.add_argument("--visual-variant", help="Variant name under subagent/ (v2 only), e.g. codex_native_gpt5_4_mini_medium")
    parser.add_argument("--run-id", help="Run folder name under problem_dir/runs/")
    parser.add_argument("--dry-run", action="store_true", help="Preview the operation without writing")
    parser.add_argument("--strict", action="store_true", help="Fail when expected state/cache files are missing")
    parser.add_argument("--no-clean", dest="clean_first", action="store_false", help="Do not clean active install first")
    parser.add_argument("--remove-runs", action="store_true", help="With --cleanup, also remove problem_dir/runs/")
    parser.set_defaults(clean_first=True)
    args = parser.parse_args()

    if args.list:
        print(json.dumps(list_variants(), indent=2))
        return

    if not args.problem_dir:
        raise SystemExit("--problem-dir is required unless --list is used")

    problem_dir = Path(args.problem_dir).resolve()
    if args.cleanup:
        result = clean_problem(problem_dir, remove_runs=args.remove_runs, dry_run=args.dry_run)
        result.update({
            "status": "dry_run" if args.dry_run else "ok",
            "problem_dir": str(problem_dir),
        })
        print(json.dumps(result, indent=2))
        return

    print(json.dumps(install(args), indent=2))


if __name__ == "__main__":
    main()
