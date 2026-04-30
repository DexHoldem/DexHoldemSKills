---
name: dexholdem-v2
description: "Agent-driven physical Texas Hold'em robot skill. Uses per-state image/action folders, visual guidelines, durable hole-card and action-sequence caches, and deterministic helpers for capture, state updates, command translation, and robot execution. Use for running or maintaining this DexHoldem workflow with Codex, Claude Code, or another coding agent."
metadata:
  author: Tianzhe Chu
  version: "0.2.0"
---

# DexHoldem Robot Skill

This skill runs a physical two-player Texas Hold'em setup with a dexterous
robot hand. The coding agent owns perception orchestration, state maintenance,
poker reasoning, and recovery decisions. Python helpers do deterministic work:
preflight, image capture, state-file updates, action translation, and robot
command dispatch, and next-move routing.

The workflow is state-folder based. Every decision is grounded in the current
state image, parsed state markdown, local caches, and the current action
sequence.

## Session Start

Run preflight from the user's working directory:

```bash
python3 skills/dexholdem-v2/scripts/preflight.py
python3 skills/dexholdem-v2/scripts/preflight.py --exp-name my_run
```

For a hardware-free smoke check:

```bash
python3 skills/dexholdem-v2/scripts/preflight.py --skip-camera --skip-remote --skip-audio
```

Preflight creates `experiments/<exp-name>/`, points `experiments/current` to
that folder, initializes `s0/` and `s_current`, copies the executable helper
scripts plus `pyproject.toml` and `config.yaml` into the experiment root, and
captures `s0/00_capture.jpg` unless camera checks are skipped.

After preflight, work from the experiment root:

```bash
cd experiments/current
python3 state.py current
```

Perform one visual pass for blind/dealer assignment using
`visual_guidelines/BLIND_BUTTON_RECOGNITION.md`, then cache the result:

```bash
python3 state.py set-blinds --dealer robot --small-blind robot --big-blind opponent --source-state s0
```

## State Contract

The experiment root contains the timeline and the durable caches:

```text
experiments/current/
  s0/
    00_capture.jpg
    01_parsed_state.md
    02_action.md
  s1/
  s_current -> s1
  hole_card_cache.json
  action_sequence.json
```

Each state folder is filled in this order:

1. `00_capture.jpg` - exact image used for visual parsing.
2. `01_parsed_state.md` - agent-authored parsed state markdown with one JSON
   block.
3. `02_action.md` - committed decision, execution result, and translated
   commands.

Create the next state only after `02_action.md` exists for the current state:

```bash
python3 state.py begin-next --after s0
```

After `02_action.md` is written, create the next state and capture a fresh
observation. This applies to ordinary poker actions, waits, continued
`acting` or `atom_idle` sequences, `to_recover` states, `show_hand`, `win`,
and `down` states that need recovery or collection. The fresh state is how the
agent verifies what physically happened.

The only normal exception is `stop`, which ends the session instead of
continuing the timeline.

## Loop Stage

`loop_stage` records the state of the robot workflow after visual parsing is
complete. Visual parsing itself is not a durable stage: the agent should wait
for vision model or vision-agent calls to finish, then write one final parsed
state for the current folder.

- `acting` - a robot atom action was dispatched recently or the hand is still
  moving. The next agent action should normally be `wait`, followed by a fresh
  capture.
- `atom_idle` - the hand has settled after an atom action, but the full
  `action_sequence.json` still has pending steps. Continue or verify that
  sequence; do not start a new poker action.
- `idle` - the full action sequence is complete, the hand is near rest pose,
  and the agent may make the next poker decision.
- `show_hand` - the opponent has shown hole cards or showdown has been reached;
  reveal the robot hole cards as needed and resolve the outcome.
- `win` - the robot has won because the opponent folded or the known showdown
  cards give the robot the stronger hand. Pull back the recognized bet chips.
- `lose` - the robot has lost because it folded or the known showdown cards
  give the opponent the stronger hand. Do not pull chips back.
- `to_recover` - the previous atom action appears to have failed harmlessly or
  had no effect after the hand settled, and the table layout is still safe
  enough to retry or repair using the cached action sequence. Examples: a hole
  card was not picked up and remains near its original position, or a chip push
  did not move the intended chip and did not disturb cards/chip layout.
- `down` - execution is failed, interrupted, blocked, or unsafe to continue
  blindly.

A completed parsed state should use one of these values.

## Caches

`hole_card_cache.json` is authoritative for hole cards because viewed cards are
returned face-down and cannot be read again from the table image. It also
stores the blind/dealer assignment recognized at session start.

`action_sequence.json` is authoritative for multi-step embodied progress. It
contains the original translator output under `plan` plus mutable step status.
Use the cached `plan` when retrying, verifying, or diagnosing the same action
sequence; do not recompute the plan from a later table state.

Useful cache helpers:

```bash
python3 state.py cache-card --slot left --card Ah --source-state s3 --confidence 0.9
python3 action_translator.py --action '{"action":"view_card","position":"left"}' --as-sequence-cache
python3 state.py start-action --sequence-json '<translator sequence-cache JSON>'
python3 state.py complete-step --step read_card
python3 state.py set-loop-stage --stage to_recover
python3 state.py set-loop-stage --stage show_hand
python3 state.py set-loop-stage --stage win
python3 state.py set-loop-stage --stage lose
python3 state.py set-loop-stage --stage atom_idle
python3 state.py set-loop-stage --stage acting
```

## Router Reference

After the current state has a capture and parsed state, the local router gives
the initial gate:

```bash
python3 router.py
```

The router returns `route`, `reason`, `agent_required`, `judged_results`, and
optional commands. It does not parse images, decide poker strategy, or declare
unsafe physical recovery by itself; those remain main-agent responsibilities.

## Visual Parsing

Do not run every file in `visual_guidelines/` on every state. Select the
smallest set needed to write a truthful `loop_stage`, `robot`, and currently
needed `table` fields. The visual model may answer in plain language; the
coding agent converts those answers into `01_parsed_state.md`.

Guideline selection:

- `SCENE_STABILITY.md` - use when deciding whether an action finished, whether
  to wait, or before any robot movement. Usually paired with recent images.
- `ROBOT_BEHAVIOR.md` - use for every state after robot/human movement, every
  embodied sequence state, and all recovery decisions.
- `TABLE_GEOMETRY.md` - use at setup, after camera/table changes, or when a
  visual agent is confused about left/right betting or inventory regions.
- `BLIND_BUTTON_RECOGNITION.md` - use during preflight or when the cached
  dealer/blind assignment is missing or visibly contradicted.
- `HELD_CARD_RECOGNITION.md` - use only when a card-view sequence is at
  `read_card` or the robot is visibly holding a readable card.
- `TURN_DETECTION.md` - use only when the state is otherwise idle/stable and a
  poker decision may be needed.
- `COMMUNITY_CARDS.md` - use when idle poker reasoning is possible, a new board
  card may have appeared, or showdown/outcome comparison is needed.
- `SHOWDOWN_OUTCOME.md` - use only when opponent cards are face-up, a fold is
  suspected, the hand reaches showdown, or `loop_stage` is `show_hand`.
- `CHIP_RECOGNITION.md` - use at setup, after chip movement/collection, or when
  chip inventory is needed for betting or next-hand state.
- `BET_RECOGNITION.md` - use before betting decisions, after bet/chip movement,
  before `collect_winnings`, or when bet counts are uncertain.

For `acting`, `atom_idle`, `to_recover`, and `down`, do not spend vision calls
on turn, community cards, inventories, or bets unless that information affects
the recovery or the pending action sequence. For `idle`, refresh the fields
needed by poker reasoning: turn, board, chip inventories, and current bets.

Keep parsed state compact:

```json
{
  "loop_stage": "idle",
  "robot": "dexterous hand is near its initial pose and not holding a card or chips",
  "table": {
    "scene_stable": true,
    "uncertain_fields": [],
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {"5": 4, "10": 3, "50": 3, "100": 3},
    "opponent_chips": {"5": 4, "10": 4, "50": 3, "100": 3},
    "my_current_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "opponent_bet": {"5": 0, "10": 0, "50": 0, "100": 0}
  }
}
```

Derived concepts such as poker street, total call amount, and turn confidence
can be inferred later from the stored cards, chip counts, and turn button
state; they do not belong in `01_parsed_state.md`.

The router uses stage-specific required fields. An `idle` state needs the full
table block shown above. Non-idle states may omit fields that were not visually
parsed and are irrelevant to the current gate, but should include
`uncertain_fields` when an omitted or unclear value matters to the next action.

For showdown, use `loop_stage` as the main compact signal. Add only small table
notes that help routing or verification, such as visible opponent hole cards;
do not store bulky hand-ranking explanations.

## Actions

Supported action JSON:

```json
{"action": "wait", "reason": "scene_unstable", "sleep_seconds": 30}
{"action": "view_card", "position": "left"}
{"action": "show_card", "position": "left"}
{"action": "put_down_card", "position": "left", "face_up": false}
{"action": "check"}
{"action": "fold"}
{"action": "call"}
{"action": "raise", "amount": 80}
{"action": "all_in"}
{"action": "collect_winnings"}
{"action": "collect_winnings", "chip_counts": {"5": 2, "10": 1, "50": 0, "100": 1}}
{"action": "request_human", "reason": "dexterous hand is holding an unreadable card"}
{"action": "stop", "reason": "session ended"}
```

Run actions through `executor.py`; use `--dry-run` to write the action and
action-sequence cache without sending robot commands.

For betting actions, the executor reads `my_chips`, `my_current_bet`, and
`opponent_bet` from the current `01_parsed_state.md` table. `call` pushes
`sum(opponent_bet) - sum(my_current_bet)`. `raise.amount` is the target total
bet after the raise, so the physical chips pushed are
`amount - sum(my_current_bet)`.

Chip actions are translated into one atom step per moved chip, such as
`push_chip_10_1` and `push_chip_5_1`, followed by `verify_idle`.

`collect_winnings` pulls chips back after a confirmed `win`. By default it
pulls `my_current_bet + opponent_bet` from the parsed table. Use
`chip_counts` only when visual parsing has a clearer explicit count for the
chips that should be pulled back.

## Recovery

Use `to_recover` when a recent robot atom failed harmlessly after the hand
settled and the current table layout is still safe to retry:

- during `view_card`, the target card was not picked up and remains face-down
  near its original position,
- during chip movement, the intended chip did not move or did not follow the
  hand, and the card/chip layout remains countable and undisturbed,
- after an atom attempt, no intended physical progress happened but no
  non-target object moved.

Use `down` when direct continuation is unsafe or unclear:

- a card was dropped during viewing,
- a returned card covers chips or hides game state,
- chip movement displaced cards, buttons, or unrelated chips,
- chip movement destroyed the table layout,
- the dexterous hand appears stuck,
- command progress is unknown,
- repeated captures remain unstable.

Request human help when a person must fix or confirm the table:

```bash
python3 state.py require-human --reason "Dexterous hand is holding an unreadable card" --resume-options mark_card,confirm_card_returned,abort_hand
```

Retry only when the cached sequence plan and recent images show that repeating
the current step is physically safe. In normal routing, that means the parsed
state should be `to_recover`; otherwise keep the state `down` and request human
help or wait for clearer evidence.

## Core Workflow

After preflight, repeat this loop from the experiment root until the action is
`stop`:

1. Capture or reuse the current state's image. If `s_current/00_capture.jpg` is
   missing, run `python3 capture.py --output s_current/00_capture.jpg`.
2. Select only the visual guidelines needed for this state, then use visual
   agents or vision models to parse the current image. Provide recent state
   images, `action_sequence.json`, and `hole_card_cache.json` when they help
   the visual agent judge motion, robot behavior, held cards, chips, bets,
   showdown, or recovery state.
3. The main coding agent summarizes the visual outputs into
   `s_current/01_parsed_state.md`. This file is the authoritative parsed state
   for the router. It must include the compact JSON block with `loop_stage`,
   `robot`, and `table`.
4. Run `python3 router.py`. Treat its JSON as the initial gating result for the
   current state.
5. Follow the gated route:
   - If the router returns a command and `agent_required: false`, run the
     command.
   - If it asks for visual parsing, repair the parsed state and rerun the
     router.
   - If it asks for held-card reading, use visual parsing to read the held card,
     update `hole_card_cache.json`, and continue the cached action sequence.
   - If it returns `recover_retryable`, use the cached `action_sequence.json`
     plan to re-execute or repair the current embodied action.
   - If it returns `recover_down`, inspect recent states and choose wait or
     `request_human`; only retry after the state is safely classified as
     `to_recover`.
   - If it returns `show_hand`, reveal robot cards as needed with `show_card`
     actions, then use `SHOWDOWN_OUTCOME.md` to decide `win`, `lose`, or keep
     resolving showdown ambiguity.
   - If it returns `collect_winnings`, execute the suggested
     `collect_winnings` action with `executor.py`.
   - If it returns `hand_lost`, do not move chips toward the robot; decide
     whether to wait for reset, request human help, clear caches for the next
     hand, or stop.
   - If it returns `choose_poker_action`, call LLM reasoning with the parsed
     table state and hole-card cache, choose the poker action, use
     `action_translator.py` if you need to inspect the new action sequence, and
     execute the action with `executor.py`.
6. Use `action_translator.py` when you need to inspect or create the action
   sequence for a new poker or embodied action. The executor also calls the
   translator internally before dispatch.
7. Use `executor.py` every time you want to send robot commands or commit an
   executable action. Do not send robot policy commands directly through
   `remote_exec.py` during normal operation. Examples:

```bash
python3 executor.py --action '{"action":"wait","reason":"not_my_turn","sleep_seconds":3}'
python3 executor.py --action '{"action":"view_card","position":"left"}'
python3 executor.py --action '{"action":"show_card","position":"left"}'
python3 executor.py --action '{"action":"put_down_card","position":"left","face_up":false}'
python3 executor.py --action '{"action":"call"}'
python3 executor.py --action '{"action":"collect_winnings"}'
python3 executor.py --action '{"action":"request_human","reason":"card was dropped"}'
```

After `executor.py` writes `02_action.md`, create the next state and capture the
next observation:

```bash
python3 state.py current
python3 state.py begin-next --after sN
python3 capture.py --output s_current/00_capture.jpg
```

Then start the loop again from visual parsing. The next image verifies what
actually happened after the last wait, retry, robot action, or human-help
request.
