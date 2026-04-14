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

## Preflight (required before each loop)

Run the preflight check. It pings the remote service and pastes `echo hello world` into the remote terminal. Do **not** start the loop if it fails.

```bash
python3 src/preflight.py
```

Expected: JSON with `"status": "ok"` and both `connection` and `type_hello_world` checks passing. Visually confirm `hello world` appeared in the remote terminal.

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
