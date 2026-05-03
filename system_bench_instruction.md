# System Bench: Quick Start

Run a full DexHoldem system-level experiment from scratch.

## Prerequisites

- Git
- Python 3.10+ (any env manager: conda, venv, pyenv, etc.)
- `uv` (for dependency sync inside the skill)
- An agent CLI: **Claude Code** (`claude`) or **Codex** (`codex`)
- A connected camera (or a source image for offline testing)

## 1. Clone the repo

```bash
git clone git@github.com:DexHoldem/DexHoldemSKills.git
cd DexHoldemSKills
```

## 2. Activate a Python environment

Any Python 3.10+ environment works. For example with conda:

```bash
conda activate base        # or your preferred env
```

The only hard Python dependency is having `uv` available on PATH (used by
preflight to sync the skill's own venv). Install it if you don't have it:

```bash
pip install uv
```

## 3. Run preflight to create the experiment workspace

Preflight sets up a self-contained experiment directory with the skill,
runtime scripts, state files, and an initial camera capture.

For the **native** skill (recommended for benchmarking — the main agent handles
all perception directly, no subagents):

```bash
python3 system_eval/preflight.py \
  --exp-name my_run \
  --native \
  --uv-sync \
  --capture-initial
```

This creates `experiments/my_run/` and symlinks `experiments/current` to it.

If you don't have a live camera, pass an existing image:

```bash
python3 system_eval/preflight.py \
  --exp-name my_run \
  --native \
  --uv-sync \
  --capture-initial \
  --camera-source path/to/image.jpg
```

Use `--force` to overwrite an existing experiment with the same name.

## 4. cd into the experiment directory

```bash
cd experiments/my_run
```

The workspace is now self-contained. The agent will find `AGENTS.md`, the
skill under `.agent/skills/dexholdem-v2-native/`, visual guidelines, runtime
scripts, and the initial state at `s0/00_capture.jpg`.

## 5. Launch the agent

### Option A: Claude Code (recommended — higher quota)

```bash
claude \
  --model claude-sonnet-4-6 \
  --effort medium
```

This opens an interactive Claude session in the experiment directory. The
agent will discover the installed skill and `AGENTS.md`, then follow the
perception-routing-execution loop described there.

For a non-interactive single-pass run:

```bash
claude -p \
  --model claude-sonnet-4-6 \
  --effort medium \
  --permission-mode acceptEdits \
  "Run the DexHoldem perception and routing loop for the current state."
```

### Option B: Codex

```bash
codex \
  --model gpt-5.4-mini \
  --reasoning medium
```

### Model recommendations

| Model             | CLI flag                        | Notes                       |
|-------------------|---------------------------------|-----------------------------|
| Claude Sonnet 4.6 | `--model claude-sonnet-4-6`     | Good balance of speed/cost  |
| Claude Opus 4.6   | `--model claude-opus-4-6`       | Higher quality, slower      |
| GPT-5.4 Mini      | `--model gpt-5.4-mini`         | Fast, lower cost via Codex  |

Use `medium` reasoning effort for all models — it gives the best
quality-to-latency tradeoff for perception tasks.

## What the agent does

Once launched, the agent follows the workflow defined in the skill:

1. **Capture** — reads `s_current/00_capture.jpg`
2. **Parse** — analyzes the image using visual guidelines, writes `01_parsed_state.md`
3. **Route** — runs `python3 router.py` to decide the next poker action
4. **Execute** — runs `python3 executor.py --action '{...}'` to command the robot
5. **Advance** — runs `python3 state.py begin-next` to create the next state folder
6. **Loop** — captures a new image and repeats

## Troubleshooting

- **`uv` not found**: Install with `pip install uv` in your active Python env.
- **Camera not available**: Use `--camera-source path/to/image.jpg` for offline testing.
- **Experiment already exists**: Add `--force` to the preflight command.
- **Agent can't find skill**: Make sure you `cd` into the experiment directory before launching.
