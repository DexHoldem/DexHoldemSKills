---
name: dexholdem-rebased
description: "Physical poker robot — native vision and reasoning loop. Captures webcam frames, extracts game state, reasons about poker strategy, executes robot actions."
metadata:
  author: Tianzhe Chu
  version: "3.0.0"
---

# DexHoldem

## Setup

Dependencies are declared in the skill-local `pyproject.toml` and installed automatically by preflight. On a fresh copy of the skill you can go straight to the Preflight step — no manual `pip install` or venv activation needed.

Manual smoke tests (optional, after preflight has installed deps):

1. `python3 src/capture.py --help` — verify capture
2. `python3 src/remote_exec.py --action calibrate` — verify remote service
3. `python3 src/remote_exec.py --action execute --command 'echo test'` — verify remote terminal

## Preflight (required before each loop)

Run the preflight check. It verifies the remote terminal, the camera, and sets up an experiment directory. Do **not** start the loop if it fails.

```bash
python3 src/preflight.py                      # auto-named experiment dir
python3 src/preflight.py --exp-name my_run    # custom name
```

Checks performed:

0. `uv_sync` — runs `uv sync` in the skill dir to install dependencies from the skill-local `pyproject.toml` (pyyaml, opencv-python, pillow) into `.venv/`. If the current interpreter lacks the deps afterwards, preflight re-execs itself under `.venv/bin/python` automatically.
1. `experiment_dir` — creates `<cwd>/experiments/<exp-name>/frames/` under the agent's current working directory and points `experiments/current` at it. Default name: `exp{YYYYMMDD}_{HHMMSS}`.
2. `camera` — captures a photo via `src/capture.py` and writes it to `<exp_dir>/frames/preflight.jpg`. **Open the file and confirm the scene looks right.**
3. `type_hello_world` — pastes `echo hello world` into the remote terminal. **Visually confirm it appeared on the remote screen.** This also covers the remote-service reachability check.
4. `move_cursor_put_down_card` — moves the remote mouse cursor to the `put_down_card` coordinates from `config.yaml` without clicking. **Visually confirm the cursor landed on the GUI button.**

Requires `uv` on PATH. On a fresh install (e.g. `playground/` created via `npx skills add`), running `python3 src/preflight.py` from inside `playground/` is enough — it bootstraps its own environment and drops the experiment dir right next to your session files.

Expected: JSON with `"status": "ok"` and all four checks passing. The created experiment dir is where subsequent state and frames for this session will be saved.

## Loop

Read `config.yaml`, `vision_prompt.md`, `prompt.md`. Preflight already created the experiment directory — do **not** run `execution_state.py init` again; it would create a second experiment and move the `current` symlink.

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
