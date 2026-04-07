---
name: dexholdem-sim
description: "Simulated poker loop — tests vision + reasoning pipeline without hardware. Uses simulator.py for game state and rendering."
metadata:
  author: Tianzhe Chu
  version: "1.0.0"
---

# DexHoldem (Simulated)

## Setup

1. Activate venv: `source .venv/bin/activate`
2. Verify simulator: `python3 simulator.py state`

## Loop

Read `vision_prompt.md`, `prompt.md`. Initialize the simulator:

```bash
python3 simulator.py state
```

The simulator manages its own game state (deck, chips, opponent AI). Each iteration:

**1. ENV** — render the current scene:

```bash
python3 -c "
from simulator import PokerSimulator
import json, sys
sim = PokerSimulator()
sim.new_hand()
sim.render('/tmp/sim_frame.jpg')
print(json.dumps(sim.get_game_state()))
"
```

Or, if continuing an existing game, call `sim.render(path)` on the active simulator instance.

**2. VISION** — `Read` the rendered image. Following `vision_prompt.md`, extract game state as JSON.

**3. ROUTE** — decide next action:

```bash
python3 skills/dexholdem-rebased/src/route.py --state '<game_state_json>'
```

Parse the JSON output and follow its `next` field:

- **`stop`** — exit loop.
- **`wait`** — sleep briefly, re-render and re-read.
- **`resume`** — should not occur in simulation; treat as wait.
- **`reason`** — proceed to step 4.

**4. REASONING** — if `route` output contains `action_hint` (`view_card` or `put_down_card`), use that action directly. Otherwise, reason about the game state using `prompt.md` with the `hand` from route output. Produce action JSON.

**5. SIMULATE** — feed action to simulator (NOT executor.py):

```bash
python3 simulator.py apply '<action_json>'
```

The simulator processes the action, updates chips/pot/community cards, runs opponent AI if needed, and advances the street. Then re-render and continue the loop.

Increment round. Continue loop.

## Key differences from dexholdem-rebased

- **No capture.py** — simulator renders images via Pillow
- **No executor.py** — actions go directly to `simulator.py apply`
- **No remote_exec** — no hardware, no network
- **Opponent AI** — simulator has built-in random opponent (call-heavy)
- **Feedback loop** — actions actually change game state for the next frame

## Supported actions

Same as `action_translator.py` inputs:

| Action | Format |
|--------|--------|
| view_card | `{"action": "view_card", "position": "left"}` |
| put_down_card | `{"action": "put_down_card"}` |
| fold | `{"action": "fold"}` |
| check | `{"action": "check"}` |
| call | `{"action": "call", "bet_chips": 10}` |
| raise | `{"action": "raise", "bet_chips": 30}` |
| all_in | `{"action": "all_in"}` |
