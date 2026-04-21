---
name: dexholdem-rebased
description: "Physical poker robot — native vision and reasoning loop. Captures webcam frames, extracts game state, reasons about poker strategy, executes robot actions."
metadata:
  author: Tianzhe Chu
  version: "3.0.0"
---

# DexHoldem

## Setup

Dependencies are declared in the skill-local `pyproject.toml` and installed into a skill-local `.venv/` by preflight (step 0, `uv_sync`). All Python commands in this skill must run under that venv — `uv` manages the venv, `uv add <pkg>` installs new deps into it.

**First-run env check (do this before anything else on a fresh clone):**

1. Check whether the skill-local venv already exists:
   ```bash
   ls skills/dexholdem-rebased/.venv/bin/python 2>/dev/null && echo "venv present" || echo "venv missing — preflight will create it"
   ```
2. Confirm `uv` is on PATH: `command -v uv` (install from https://docs.astral.sh/uv/ if missing).
3. If the venv is missing, the first `python3 src/preflight.py` run will create it via `uv sync` and re-exec itself into `.venv/bin/python` automatically. No manual `pip install` or `source .venv/bin/activate` needed.
4. If the venv is present but you added a new dependency, run `uv add <pkg>` from the skill dir — do not `pip install` into the venv directly.

Manual smoke tests (optional, after preflight has installed deps):

1. `python3 src/capture.py --help` — verify capture
2. `python3 src/remote_exec.py --action calibrate` — verify remote service
3. `python3 src/remote_exec.py --action execute --command 'echo test'` — verify remote terminal

## Preflight (required before each loop)

Run the preflight check. It verifies the remote terminal, the camera, and sets up an experiment directory. Do **not** start the loop if it fails.

**Run preflight from the user's main project folder** — the CWD at invocation time determines where `experiments/<exp-name>/` is created. Do **not** run it from inside a hidden agent dir like `.claude/`, `.agent/`, or any other tool-internal scratch dir; those are not meant to hold session artifacts and will hide the experiment from the user. If your CWD is a hidden agent dir, `cd` up to the project root first.

```bash
python3 src/preflight.py                      # auto-named experiment dir
python3 src/preflight.py --exp-name my_run    # custom name
```

Checks performed:

0. `uv_sync` — runs `uv sync` in the skill dir to install dependencies from the skill-local `pyproject.toml` (pyyaml, opencv-python, pillow) into `.venv/`. If the current interpreter lacks the deps afterwards, preflight re-execs itself under `.venv/bin/python` automatically.
1. `experiment_dir` — creates `<cwd>/experiments/<exp-name>/frames/` under the agent's current working directory and points `experiments/current` at it. Default name: `exp{YYYYMMDD}_{HHMMSS}`.
2. `camera` — captures a photo via `src/capture.py` and writes it to `<exp_dir>/frames/preflight.jpg`. **Open the file and confirm the scene looks right.**
3. `type_hello_world` — pastes `echo hello world` into the remote terminal. **Visually confirm it appeared on the remote screen.** This also covers the remote-service reachability check.
4. `move_cursor_reset_hand` — moves the remote mouse cursor to the `reset_hand` coordinates from `config.yaml` (the GUI button that resets the dexterous hand to init state) without clicking. **Visually confirm the cursor landed on the reset button.**
5. `audio` — verifies `ffplay` is on PATH and every file listed under `config.audio.files` exists in `audio/`. Required for BGM + SFX (see Loop → Audio below).

Requires `uv` on PATH. On a fresh install (e.g. `playground/` created via `npx skills add`), running `python3 src/preflight.py` from inside `playground/` is enough — it bootstraps its own environment and drops the experiment dir right next to your session files.

Expected: JSON with `"status": "ok"` and all five checks passing. The created experiment dir is where subsequent state and frames for this session will be saved.

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

The executor automatically runs a **pre-action stage** before dispatching commands, declared by the translator:
- For most actions (view, bet/call/raise, all-in): send Ctrl+C then click the `reset_hand` button and wait for the arm to settle at init pose.
- For `put_down_card` (the arm is currently holding a card): send Ctrl+C only — **no** reset click, because reset would drop the card.
- For placeholders (`check`, `fold`): no stage.

After a successful `view_card`, the executor locks the next round to `put_down_card` at the same position (see prompt.md action-space constraints). Increment round. Continue loop.

## Audio (BGM + SFX)

`route.py` and `executor.py` also fire audio hooks via `src/bgm.py` — a local ffplay-based BGM manager. The reasoning LLM does **not** need to manage audio; it's a pure side-effect of game-phase and action transitions:

- **BGM (looping)** — `start.mp4` loops when a hand is active; `allin.mp4` replaces it when the agent goes all-in.
- **One-shots** — folding plays `lose.mp4` and stops BGM; reaching `game_over` plays `win.mp4` and stops BGM.
- **SFX prefixes** — `view_card` is prefixed with `wyyp.mp3`, `put_down_card` face-down with `pmywt.mp3`, and every action has a `taunt_chance` (default 0.2) of also playing `gwcpx.mp3`.

All files and the taunt probability live in `config.yaml` → `audio:`. Set `audio.enabled: false` to mute everything without touching the code. Playback is local (agent machine), so speakers on the loop host must be within earshot of the table.
