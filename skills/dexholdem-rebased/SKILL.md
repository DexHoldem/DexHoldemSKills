---
name: dexholdem-rebased
description: "Physical poker robot — native vision and reasoning loop. Captures webcam frames, extracts game state, reasons about poker strategy, executes robot actions."
metadata:
  author: Tianzhe Chu
  version: "3.0.0"
---

# DexHoldem

## Setup

1. Activate venv: `source .venv/bin/activate`
2. `python3 src/capture.py --help` — verify capture
3. `python3 src/remote_exec.py --action calibrate` — verify remote service
4. `python3 src/remote_exec.py --action execute --command 'echo test'` — verify remote terminal

## Loop

Read `config.yaml`, `vision_prompt.md`, `prompt.md`. Initialize:

```bash
python3 src/execution_state.py init
```

Each iteration:

**1. ENV** — capture a frame:

```bash
python3 src/capture.py
python3 src/execution_state.py save-frame <image_path> --round <N> --label capture
```

**2. VISION** — `Read` the previous frame and current frame. Following `vision_prompt.md`, extract game state as JSON.

**3. ROUTE** — decide next action:

```bash
python3 src/route.py --state '<game_state_json>'
```

Parse the JSON output and follow its `next` field:

- **`stop`** — exit loop.
- **`wait`** — sleep `loop.poll_interval` seconds, continue.
- **`resume`** — cancel interrupted execution and recapture:
  ```bash
  python3 src/executor.py --cancel-previous
  ```
- **`reason`** — proceed to step 4.

**4. REASONING** — if `route` output contains `action_hint` (`view_card` or `put_down_card`), use that action directly. Otherwise, reason about the game state using `prompt.md` with the `hand` from route output. Produce action JSON.

**5. EXECUTE**:

```bash
python3 src/executor.py --action '<action_json>' [--chips '<chips_json>']
```

Increment round. Continue loop.

## Dry Run (no hardware, no images)

For testing the routing and reasoning pipeline without hardware or image rendering, use `vision_prompt_dryrun.md` instead of `vision_prompt.md`. This prompt asks the LLM to generate game state JSON directly.

**Loop:**

1. **VISION** — follow `vision_prompt_dryrun.md` with no prior state. The model generates an opening game state (preflop, blinds posted).
2. **ROUTE** — `python3 src/route.py --state '<game_state_json>'`
3. **REASONING** — action_hint or poker reasoning via `prompt.md`.
4. **EXECUTE** — `python3 src/executor.py --action '<action_json>' --dry-run`
5. **VISION** — follow `vision_prompt_dryrun.md` with the previous state + action taken. The model simulates the next state.
6. Repeat 2–5.

Steps 1 (ENV/capture) and image reading are skipped entirely. No Pillow dependency.
