# System Bench: Quick Start

Run a full DexHoldem system-level experiment from scratch.

## Prerequisites

- Git
- `uv` (usually pre-installed; handles Python and dependency management)
- An agent CLI: **Claude Code** (`claude`) or **Codex** (`codex`)
- Node.js 18+ (for the monitor dashboard, optional but recommended)
- A connected camera (or a source image for offline testing)

## 1. Clone the repo

```bash
git clone git@github.com:DexHoldem/DexHoldemSKills.git
cd DexHoldemSKills
```

## 2. Create a Python environment with uv

```bash
uv venv --python 3.12
source .venv/bin/activate
```

This creates a local `.venv` and activates it. `uv` will also manage
dependencies inside the skill during preflight (`--uv-sync`).

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

For the **mix** skill (native perception plus per-instruction robot-client
ports/models):

```bash
python3 system_eval/preflight.py \
  --exp-name my_run \
  --mix \
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

### Prompting the agent

Once the agent session is open, prompt it to start the game loop:

> Start a dexholdem-v2-native game loop

The agent will read `AGENTS.md` and the skill docs, then begin the
capture-parse-route-execute cycle autonomously.

## What the agent does

Once launched, the agent follows the workflow defined in the skill:

1. **Capture** — reads `s_current/00_capture.jpg`
2. **Parse** — analyzes the image using visual guidelines, writes `01_parsed_state.md`
3. **Route** — runs `python3 router.py` to decide the next poker action
4. **Execute** — runs `python3 executor.py --action '{...}'` to command the robot
5. **Advance** — runs `python3 state.py begin-next` to create the next state folder
6. **Loop** — captures a new image and repeats

## 6. Monitor the experiment (optional)

The repo includes a real-time monitoring dashboard that watches the experiment
directory and displays live state updates in the browser.

### Setup (one-time)

```bash
cd monitor-server
npm install
npm run build
cd ..
```

### Start the monitor

Point the monitor at the exact experiment directory that preflight created.
For example, if you ran `--exp-name my_run`, the experiment lives at
`experiments/my_run/`:

```bash
npm start --prefix monitor-server -- --exp-dir ./experiments/my_run
```

Then open `http://localhost:3000` in your browser.

You can also monitor the entire `experiments/` parent directory (picks up
all experiments):

```bash
npm start --prefix monitor-server -- --exp-dir ./experiments
```

Alternatively, you can ask an agent (Claude or Codex) to start the monitor
for you. From the repo root, prompt the agent:

> Start the DexHoldem monitor server watching experiments/my_run.

The agent will run the `npm start` command with the correct `--exp-dir`
flag. Make sure the path matches the experiment created by preflight —
the monitor needs to watch the directory containing `action_sequence.json`,
`s_current/`, and the state folders to display live updates.

### What it shows

- **Live state tracking** — current loop stage (idle, acting, recovering, etc.)
  and activity (capturing, perceiving, reasoning, acting)
- **Capture preview** — the latest camera screenshot from the experiment
- **Table state** — chip counts, bets, community cards, turn indicator
- **Safety counters** — consecutive waits, recoveries, executor failures
- **Human help alerts** — pulsing red indicator when the agent requests
  human intervention, with the reason and resume options displayed

The dashboard uses WebSocket for real-time updates — whenever the agent writes
a new state file, capture, or action sequence, the monitor reflects it
immediately.

### Human help workflow

When the agent gets stuck and requests human help:

1. The monitor shows a pulsing "Requesting Human" alert with the reason
2. Resolve the physical issue (e.g. fix a dropped chip, reposition a card)
3. Acknowledge and resume:

```bash
cd experiments/my_run
python3 state.py ack-human-help --reset-safety --set-stage to_recover
```

The agent will then re-capture and continue.

## Troubleshooting

- **`uv` not found**: Install with `pip install uv` in your active Python env.
- **Camera not available**: Use `--camera-source path/to/image.jpg` for offline testing.
- **Experiment already exists**: Add `--force` to the preflight command.
- **Agent can't find skill**: Make sure you `cd` into the experiment directory before launching.
