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
SKILL_SOURCE_NATIVE = ROOT / "skills" / "dexholdem-v2-native"
SKILL_SOURCE_BACKEND = ROOT / "skills" / "dexholdem-v2-backend-preview"
SKILL_SOURCE_ISOLATED = ROOT / "skills" / "dexholdem-v2-isolated"
SUBAGENT_ROOT = ROOT / "subagent"
BACKEND_CODEX_AGENT_SOURCE = SUBAGENT_ROOT / "backend" / "dexholdem_backend_perceiver.toml"
ISOLATED_CODEX_AGENT_SOURCE = SUBAGENT_ROOT / "isolated" / "visual_agent.toml"
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
BACKEND_RUNTIME_FILES = RUNTIME_FILES + ("perception_stream.py",)


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


def backend_agent_files() -> list[Path]:
    if not BACKEND_CODEX_AGENT_SOURCE.exists():
        raise SystemExit(f"backend Codex agent does not exist: {BACKEND_CODEX_AGENT_SOURCE}")
    return [BACKEND_CODEX_AGENT_SOURCE]


def isolated_agent_files() -> list[Path]:
    if not ISOLATED_CODEX_AGENT_SOURCE.exists():
        raise SystemExit(f"isolated Codex agent does not exist: {ISOLATED_CODEX_AGENT_SOURCE}")
    return [ISOLATED_CODEX_AGENT_SOURCE]


def selected_skill_name(native: bool = False, backend: bool = False, isolated: bool = False) -> str:
    if backend:
        return "dexholdem-v2-backend-preview"
    if isolated:
        return "dexholdem-v2-isolated"
    if native:
        return "dexholdem-v2-native"
    return "dexholdem-v2"


def selected_skill_source(native: bool = False, backend: bool = False, isolated: bool = False) -> Path:
    if backend:
        return SKILL_SOURCE_BACKEND
    if isolated:
        return SKILL_SOURCE_ISOLATED
    if native:
        return SKILL_SOURCE_NATIVE
    return SKILL_SOURCE


def selected_runtime_files(backend: bool = False) -> tuple[str, ...]:
    return BACKEND_RUNTIME_FILES if backend else RUNTIME_FILES


def install_agent_files(files: list[Path], target_dir: Path) -> list[dict]:
    target_dir.mkdir(parents=True, exist_ok=True)
    installed = []
    for src in files:
        dest = target_dir / src.name
        shutil.copy2(src, dest)
        installed.append({"name": src.stem, "source": str(src.relative_to(ROOT)), "path": str(dest)})
    return installed


def install_skill(exp_dir: Path, native: bool = False, backend: bool = False, isolated: bool = False) -> dict:
    skill_name = selected_skill_name(native=native, backend=backend, isolated=isolated)
    skill_source = selected_skill_source(native=native, backend=backend, isolated=isolated)
    shared_skill = exp_dir / ".agent" / "skills" / skill_name
    copytree_clean(skill_source, shared_skill)

    links = {}
    for link in (
        exp_dir / ".claude" / "skills" / skill_name,
        exp_dir / ".codex" / "skills" / skill_name,
    ):
        replace_symlink(link, relative_target(link, shared_skill))
        links[str(link.relative_to(exp_dir))] = os.readlink(link)

    agents_link = exp_dir / ".agents"
    replace_symlink(agents_link, ".agent")
    links[str(agents_link.relative_to(exp_dir))] = os.readlink(agents_link)

    return {"shared_skill": str(shared_skill), "skill_name": skill_name, "links": links}


def expose_runtime(exp_dir: Path, native: bool = False, backend: bool = False, isolated: bool = False) -> dict:
    skill_name = selected_skill_name(native=native, backend=backend, isolated=isolated)
    skill_dir = exp_dir / ".agent" / "skills" / skill_name
    exposed = []
    for name in selected_runtime_files(backend=backend):
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

    return {"runtime_entries": exposed, "skill_name": skill_name}


def run_uv_sync(exp_dir: Path, native: bool = False, backend: bool = False, isolated: bool = False) -> dict:
    skill_name = selected_skill_name(native=native, backend=backend, isolated=isolated)
    skill_dir = exp_dir / ".agent" / "skills" / skill_name
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


def capture_initial(exp_dir: Path, source: str | None = None, native: bool = False, backend: bool = False, isolated: bool = False) -> dict:
    output = exp_dir / "s0" / "00_capture.jpg"
    if source:
        source_path = Path(source)
        if not source_path.is_absolute():
            source_path = (ROOT / source_path).resolve()
        if not source_path.exists():
            raise SystemExit(f"camera source does not exist: {source_path}")
        shutil.copy2(source_path, output)
        return {"mode": "source_copy", "source": str(source_path), "output": str(output)}

    skill_name = selected_skill_name(native=native, backend=backend, isolated=isolated)
    venv_python = exp_dir / ".agent" / "skills" / skill_name / ".venv" / "bin" / "python"
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


AGENTS_MD_NATIVE_TEMPLATE = """# DexHoldem System Evaluation (Native)

This experiment workspace is configured for native system-level DexHoldem runs.
The main agent handles all perception directly without delegating to subagents.

## Skill Overview

The DexHoldem native skill (`dexholdem-v2-native`) runs a physical two-player
Texas Hold'em setup with a dexterous robot hand. The main agent handles:
- Visual perception directly (using visual guidelines)
- State maintenance and interpretation
- Poker reasoning and action decisions
- Recovery decisions when errors occur

### Key Files

- `SKILL.md` - Full skill documentation (in `.agent/skills/dexholdem-v2-native/`)
- `visual_guidelines/` - Visual parsing reference documents
- `config.yaml` - Robot and camera configuration
- `state.py` - State management CLI
- `router.py` - Next-move routing logic
- `executor.py` - Robot action execution
- `capture.py` - Camera capture utility

### State Contract

```
experiments/current/
  s0/                      # First state folder
    00_capture.jpg         # Screenshot
    01_parsed_state.md     # Parsed visual state (agent writes)
    02_action.md           # Committed action (agent writes)
  s1/, s2/, ...            # Subsequent states
  s_current -> s<N>        # Symlink to current state
  hole_card_cache.json     # Cached hole cards
  action_sequence.json     # Current action sequence and safety counters
```

### Visual Guidelines

Use these files in `visual_guidelines/` for direct image parsing:

| Guideline | Purpose |
|-----------|---------|
| `SCENE_STABILITY.md` | Check if scene is stable for action |
| `ROBOT_BEHAVIOR.md` | Describe robot/dexterous hand state |
| `TABLE_GEOMETRY.md` | Robot/opponent orientation, zones |
| `TURN_DETECTION.md` | Determine whose turn it is |
| `BLIND_BUTTON_RECOGNITION.md` | Identify dealer and blind positions |
| `COMMUNITY_CARDS.md` | Identify community cards on board |
| `CHIP_RECOGNITION.md` | Count remaining inventory chips |
| `BET_RECOGNITION.md` | Count current bet chips |
| `HELD_CARD_RECOGNITION.md` | Read cards held by robot |
| `SHOWDOWN_OUTCOME.md` | Determine winner at showdown |

### Core Workflow

1. **Capture** - `python3 capture.py` takes a screenshot
2. **Parse** - Read image directly using visual guidelines, write `01_parsed_state.md`
3. **Route** - `python3 router.py` determines next action
4. **Execute** - `python3 executor.py --action '<json>'` runs robot commands
5. **Advance** - `python3 state.py begin-next` creates the next state folder

### Common Commands

```bash
python3 state.py current                    # Show current state info
python3 state.py begin-next                 # Advance to next state
python3 capture.py --output s<N>/00_capture.jpg  # Capture image
python3 router.py                           # Get routing decision
python3 executor.py --action '{{...}}'       # Execute action
```
"""

AGENTS_MD_BACKEND_TEMPLATE = """# DexHoldem System Evaluation (Backend Stream)

This experiment workspace is configured for backend-stream DexHoldem runs.
The main agent owns the canonical game loop and robot actions. A background
Codex perceiver keeps a `/tmp` perception stream warm for capture and visual
parse reuse.

## Skill Overview

The DexHoldem backend skill (`dexholdem-v2-backend-preview`) runs a physical two-player
Texas Hold'em setup with a dexterous robot hand. The main agent handles:
- Canonical state ownership and perception imports
- State maintenance and interpretation
- Poker reasoning and action decisions
- Recovery decisions when errors occur

The visible Codex backend perceiver handles only background capture/parsing:

- `dexholdem_backend_perceiver` in `.codex/agents/`

### Key Files

- `SKILL.md` - Full skill documentation (in `.agent/skills/dexholdem-v2-backend-preview/`)
- `visual_guidelines/` - Visual parsing reference documents
- `config.yaml` - Robot and camera configuration
- `state.py` - State management CLI
- `router.py` - Next-move routing logic
- `executor.py` - Robot action execution
- `capture.py` - Camera capture utility
- `perception_stream.py` - /tmp perception stream import helper

### Core Workflow

0. **Start backend** - call `dexholdem_backend_perceiver` with the experiment root
1. **Import perception** - `python3 perception_stream.py import-latest --max-age-seconds 90`
2. **Fallback parse** - if import fails, capture/parse directly with visual guidelines
3. **Route** - `python3 router.py` determines next action
4. **Execute** - `python3 executor.py --action '<json>'` runs robot commands
5. **Advance** - `python3 state.py begin-next` creates the next state folder

### Common Commands

```bash
python3 state.py current                    # Show current state info
python3 state.py begin-next                 # Advance to next state
python3 perception_stream.py root --mkdir   # Show/create /tmp stream root
python3 perception_stream.py import-latest --max-age-seconds 90
python3 capture.py --output s<N>/00_capture.jpg  # Direct fallback capture
python3 router.py                           # Get routing decision
python3 executor.py --action '{{...}}'       # Execute action
```
"""

AGENTS_MD_ISOLATED_TEMPLATE = """# DexHoldem System Evaluation (Isolated Perception)

This experiment workspace is configured for isolated-perception DexHoldem runs.
The main agent owns routing, state maintenance, poker reasoning, robot actions,
and recovery decisions. The visible Codex `visual_agent` owns captured-state
visual parsing and writes `s_current/01_parsed_state.md`.

## Skill Overview

The DexHoldem isolated skill (`dexholdem-v2-isolated`) runs a physical
two-player Texas Hold'em setup with a dexterous robot hand. The main agent
captures images, calls the isolated visual subagent, validates the parsed-state
file, then routes and executes actions.

The visible Codex isolated perceiver is:

- `visual_agent` in `.codex/agents/`

### Key Files

- `SKILL.md` - Full skill documentation (in `.agent/skills/dexholdem-v2-isolated/`)
- `visual_guidelines/` - Visual parsing reference documents passed by path
- `state.py` - State management CLI
- `router.py` - Next-move routing logic
- `executor.py` - Robot action execution
- `capture.py` - Camera capture utility

### Core Workflow

1. **Capture** - `python3 capture.py` takes a screenshot
2. **Delegate parse** - call `visual_agent` with capture/output/cache/guideline paths
3. **Validate parse** - confirm `s_current/01_parsed_state.md` has a table JSON object
4. **Route** - `python3 router.py` determines next action
5. **Execute** - `python3 executor.py --action '<json>'` runs robot commands
6. **Advance** - `python3 state.py begin-next` creates the next state folder
"""

AGENTS_MD_TEMPLATE = """# DexHoldem System Evaluation

This experiment workspace is configured for real system-level DexHoldem runs.

## Skill Overview

The DexHoldem skill (`dexholdem-v2`) runs a physical two-player Texas Hold'em
setup with a dexterous robot hand. The main agent owns:
- Perception orchestration (via visual subagents)
- State maintenance and interpretation
- Poker reasoning and action decisions
- Recovery decisions when errors occur

Python helpers handle deterministic work: image capture, state-file updates,
action translation, and robot command dispatch.

### Key Files

- `SKILL.md` - Full skill documentation (in `.agent/skills/dexholdem-v2/`)
- `visual_guidelines/` - Visual parsing reference documents
- `config.yaml` - Robot and camera configuration
- `state.py` - State management CLI
- `router.py` - Next-move routing logic
- `executor.py` - Robot action execution
- `capture.py` - Camera capture utility

### State Contract

```
experiments/current/
  s0/                      # First state folder
    00_capture.jpg         # Screenshot
    01_parsed_state.md     # Parsed visual state (agent writes)
    02_action.md           # Committed action (agent writes)
  s1/, s2/, ...            # Subsequent states
  s_current -> s<N>        # Symlink to current state
  hole_card_cache.json     # Cached hole cards (persists across states)
  action_sequence.json     # Current action sequence and safety counters
```

### Core Workflow

1. **Capture** - `python3 capture.py` takes a screenshot to `s<N>/00_capture.jpg`
2. **Parse** - Visual subagents analyze the image, main agent writes `01_parsed_state.md`
3. **Route** - `python3 router.py` determines next action based on state
4. **Execute** - `python3 executor.py --action '<json>'` runs robot commands
5. **Advance** - `python3 state.py begin-next` creates the next state folder

### Common Commands

```bash
python3 state.py current                    # Show current state info
python3 state.py begin-next                 # Advance to next state
python3 capture.py --output s<N>/00_capture.jpg  # Capture image
python3 router.py                           # Get routing decision
python3 executor.py --action '{{...}}'       # Execute action
python3 state.py require-human --reason "..." # Request human help
python3 state.py ack-human-help             # Clear human help request
```

---

## Available Visual Subagents

Split visual subagents are installed for image perception tasks.

### Codex Agents (.codex/agents/)

{codex_agents}

### Claude Agents (.claude/agents/)

{claude_agents}

### Subagent Responsibilities

| Agent | Purpose |
|-------|---------|
| `chip_recognition_agent` | Count remaining inventory chips (not bets) |
| `bet_recognition_agent` | Count current bet chips in betting areas |
| `community_cards_agent` | Identify community cards on the board |
| `turn_detection_agent` | Determine whose turn it is |
| `blind_button_recognition_agent` | Identify dealer button and blind positions |
| `scene_stability_agent` | Check if the scene is stable for action |
| `robot_behavior_agent` | Describe robot/dexterous hand state |
| `held_card_recognition_agent` | Read cards held by the robot (when visible) |
| `showdown_outcome_agent` | Determine winner at showdown (when applicable) |

### Usage Guidelines

- Delegate image-reading questions to the appropriate scoped visual agent
- Run independent visual subagents **in parallel** when possible
- Visual subagents are **read-only** - they return evidence, never write state
- The main agent merges subagent outputs and writes `01_parsed_state.md`
- Refer to `visual_guidelines/` for detailed parsing rules
"""


def generate_agents_md(
    codex_files: list[Path],
    claude_files: list[Path],
    native: bool = False,
    backend: bool = False,
    isolated: bool = False,
) -> str:
    if backend:
        return AGENTS_MD_BACKEND_TEMPLATE
    if isolated:
        return AGENTS_MD_ISOLATED_TEMPLATE
    if native:
        return AGENTS_MD_NATIVE_TEMPLATE
    codex_list = "\n".join(f"- `{f.stem}` ({f.name})" for f in codex_files)
    claude_list = "\n".join(f"- `{f.stem}` ({f.name})" for f in claude_files)
    return AGENTS_MD_TEMPLATE.format(
        codex_agents=codex_list or "(none)",
        claude_agents=claude_list or "(none)",
    )


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
    skill_source = selected_skill_source(native=args.native, backend=args.backend, isolated=args.isolated)
    skill_name = selected_skill_name(native=args.native, backend=args.backend, isolated=args.isolated)
    manifest = {
        "schema_version": 1,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": {
            "name": args.exp_name,
            "root": str(exp_dir),
            "current_link": str(exp_dir.parent / "current"),
        },
        "defaults": {
            "native": args.native,
            "backend": args.backend,
            "isolated": args.isolated,
            "skill": skill_name,
            "visual_setting": "backend_stream_native" if args.backend else "isolated" if args.isolated else "native" if args.native else "split",
            "codex_variant": args.codex_variant if not args.native and not args.backend and not args.isolated else None,
            "claude_variant": args.claude_variant if not args.native and not args.backend and not args.isolated else None,
        },
        "source": {
            "skill": str(skill_source.relative_to(ROOT)),
            "skill_files": tree_records(skill_source),
        },
    }
    if args.backend:
        manifest["source"]["codex_backend_agents"] = [file_record(path) for path in codex_files]
    elif args.isolated:
        manifest["source"]["codex_isolated_agents"] = [file_record(path) for path in codex_files]
    elif not args.native:
        manifest["source"]["codex_subagents"] = [file_record(path) for path in codex_files]
        manifest["source"]["claude_subagents"] = [file_record(path) for path in claude_files]
        manifest["model_checks"] = model_checks(codex_files, claude_files)
    return manifest


def create_experiment(args: argparse.Namespace) -> dict:
    selected_modes = [args.native, args.backend, args.isolated]
    if sum(1 for value in selected_modes if value) > 1:
        raise SystemExit("--native, --backend, and --isolated are mutually exclusive")
    validate_exp_name(args.exp_name)
    experiments_root = Path(args.experiments_root).resolve()
    exp_dir = experiments_root / args.exp_name

    codex_files: list[Path] = []
    claude_files: list[Path] = []
    if args.backend:
        codex_files = backend_agent_files()
    elif args.isolated:
        codex_files = isolated_agent_files()
    elif not args.native:
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
    skill_result = install_skill(exp_dir, native=args.native, backend=args.backend, isolated=args.isolated)
    runtime_result = expose_runtime(exp_dir, native=args.native, backend=args.backend, isolated=args.isolated)
    uv_result = run_uv_sync(
        exp_dir,
        native=args.native,
        backend=args.backend,
        isolated=args.isolated,
    ) if args.uv_sync else {"skipped": True}
    state_result = init_state(exp_dir)
    capture_result = capture_initial(
        exp_dir,
        args.camera_source,
        native=args.native,
        backend=args.backend,
        isolated=args.isolated,
    ) if args.capture_initial else {"skipped": True}

    codex_installed: list[dict] = []
    claude_installed: list[dict] = []
    visible_codex: list[str] = []
    visible_claude: list[str] = []

    if args.backend:
        codex_installed = install_agent_files(codex_files, exp_dir / ".codex" / "agents")
        visible_codex = [f.stem for f in codex_files]
    elif args.isolated:
        codex_installed = install_agent_files(codex_files, exp_dir / ".codex" / "agents")
        visible_codex = [f.stem for f in codex_files]
    elif not args.native:
        codex_installed = install_agent_files(codex_files, exp_dir / ".codex" / "agents")
        claude_installed = install_agent_files(claude_files, exp_dir / ".claude" / "agents")
        visible_codex = [f.stem for f in codex_files]
        visible_claude = [f.stem for f in claude_files]

    agents_md = generate_agents_md(
        codex_files,
        claude_files,
        native=args.native,
        backend=args.backend,
        isolated=args.isolated,
    )
    (exp_dir / "AGENTS.md").write_text(agents_md)

    if not args.no_current:
        replace_symlink(exp_dir.parent / "current", exp_dir)

    manifest.update({
        "installed": {
            "skill": skill_result,
            "runtime": runtime_result,
            "uv_sync": uv_result,
            "state": state_result,
            "capture": capture_result,
        },
    })
    if args.backend:
        manifest["installed"]["codex_agents"] = codex_installed
        manifest["visible_agents"] = {
            "codex": visible_codex,
            "claude": visible_claude,
            "codex_dir": ".codex/agents",
            "claude_dir": ".claude/agents",
        }
    elif args.isolated:
        manifest["installed"]["codex_agents"] = codex_installed
        manifest["visible_agents"] = {
            "codex": visible_codex,
            "claude": visible_claude,
            "codex_dir": ".codex/agents",
            "claude_dir": ".claude/agents",
        }
    elif not args.native:
        manifest["installed"]["codex_agents"] = codex_installed
        manifest["installed"]["claude_agents"] = claude_installed
        manifest["visible_agents"] = {
            "codex": visible_codex,
            "claude": visible_claude,
            "codex_dir": ".codex/agents",
            "claude_dir": ".claude/agents",
        }
    (exp_dir / "system_eval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    return {"status": "ok", "experiment": str(exp_dir), "manifest": manifest}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp-name", required=True, help="Experiment directory name to create")
    parser.add_argument("--experiments-root", default=str(DEFAULT_EXPERIMENTS_ROOT))
    parser.add_argument("--native", action="store_true", help="Use dexholdem-v2-native skill (no subagents)")
    parser.add_argument("--backend", action="store_true", help="Use dexholdem-v2-backend-preview skill with a background Codex perception stream")
    parser.add_argument("--isolated", action="store_true", help="Use dexholdem-v2-isolated skill with a single visual_agent subagent")
    parser.add_argument("--codex-variant", default=DEFAULT_CODEX_VARIANT)
    parser.add_argument("--claude-variant", default=DEFAULT_CLAUDE_VARIANT)
    parser.add_argument("--force", action="store_true", help="Replace an existing experiment directory")
    parser.add_argument("--dry-run", action="store_true", help="Print the planned setup without writing files")
    parser.add_argument("--no-current", action="store_true", help="Do not update experiments/current")
    parser.add_argument("--capture-initial", action="store_true", help="Capture s0/00_capture.jpg after setup")
    parser.add_argument("--camera-source", help="With --capture-initial, copy an existing image as s0/00_capture.jpg")
    parser.add_argument("--uv-sync", action="store_true", help="Run uv sync in the copied skill")
    args = parser.parse_args()

    print(json.dumps(create_experiment(args), indent=2))


if __name__ == "__main__":
    main()
