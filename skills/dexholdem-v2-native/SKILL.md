---
name: dexholdem-v2-native
description: "Native agent-driven physical Texas Hold'em robot skill for system benchmarks. The main agent handles perception directly using visual guidelines, without delegating to subagents. Use for system-level evaluation where one agent handles the full workflow."
metadata:
  author: Tianzhe Chu
  version: "0.2.0"
---

# DexHoldem Robot Skill (Native)

This skill runs a physical two-player Texas Hold'em setup with a dexterous
robot hand. The main agent owns perception, state maintenance, poker reasoning,
and recovery decisions directly. Python helpers do deterministic work:
preflight, image capture, state-file updates, action translation, and robot
command dispatch.

This native variant is designed for system benchmarks where the main agent
handles visual parsing directly rather than delegating to subagents.

## Session Start

From the user's working directory, expose the helper scripts:

```bash
ln -s .agents/skills/dexholdem-v2-native/scripts/*.py ./
```

For Claude installations:

```bash
ln -s .claude/skills/dexholdem-v2-native/scripts/*.py ./
```

Then run preflight:

```bash
python3 preflight.py
python3 preflight.py --exp-name my_run
```

For a hardware-free smoke check:

```bash
python3 preflight.py --skip-camera --skip-remote --skip-audio
```

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

Blind amounts: small blind = 5, big blind = 10.

## Preflop Blind Posting

At the start of each hand, the robot must post its blind if it is the small
blind or big blind:

- If robot is **small blind**: push a 5-chip to the betting area.
- If robot is **big blind**: push a 10-chip to the betting area.

This is a forced bet. Post the blind immediately after confirming the
blind/dealer assignment, before or right after viewing hole cards:

1. Recognize and cache blind/dealer assignment.
2. Post the robot's blind chip.
3. View hole cards.
4. Continue preflop betting.

Use `{"action": "raise", "amount": 5}` for small blind or
`{"action": "raise", "amount": 10}` for big blind.

## State Contract

The experiment root contains the timeline and durable caches:

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

Each state folder is filled in order:

1. `00_capture.jpg` - image used for visual parsing.
2. `01_parsed_state.md` - agent-authored parsed state with JSON block.
3. `02_action.md` - committed decision and execution result.

Create the next state only after `02_action.md` exists:

```bash
python3 state.py begin-next --after s0
```

## Loop Stage

`loop_stage` records the robot workflow state after visual parsing:

- `acting` - robot atom dispatched or hand still moving; next action is `wait`.
- `atom_idle` - hand settled after atom but sequence has pending steps.
- `idle` - sequence complete, hand at rest, agent may make next poker decision.
- `show_hand` - showdown reached; reveal robot cards and resolve outcome.
- `win` - robot won; pull back recognized bet chips.
- `lose` - robot lost; do not pull chips back.
- `to_recover` - previous atom failed harmlessly, safe to retry.
- `down` - unsafe to continue; request human help.

## Caches

`hole_card_cache.json` is authoritative for hole cards and blind/dealer assignment.

`action_sequence.json` is authoritative for multi-step embodied progress.

Useful cache helpers:

```bash
python3 state.py cache-card --slot left --card Ah --source-state s3 --confidence 0.9
python3 action_translator.py --action '{"action":"view_card","position":"left"}' --as-sequence-cache
python3 state.py start-action --sequence-json '<translator sequence-cache JSON>'
python3 state.py dispatch-step --step pick_card
python3 state.py complete-step --step read_card
python3 state.py prepare-retry --step push_chip_10_1 --reason to_recover
python3 state.py next-hand
python3 state.py set-loop-stage --stage to_recover
```

## Router Reference

After the current state has a capture and parsed state:

```bash
python3 router.py
```

The router returns `route`, `reason`, `agent_required`, `judged_results`, and
optional commands.

## Visual Parsing

Use the files in `visual_guidelines/` to write a truthful `loop_stage`, `robot`,
and table fields. The agent reads images directly and applies the appropriate
guideline for each visual question.

Guideline purposes:

- `SCENE_STABILITY.md` - action completion, waiting decisions, movement checks.
- `ROBOT_BEHAVIOR.md` - hand pose, motion, held objects, safety, recovery.
- `TABLE_GEOMETRY.md` - robot/opponent orientation, zones, camera layout.
- `BLIND_BUTTON_RECOGNITION.md` - dealer, small blind, big blind buttons.
- `HELD_CARD_RECOGNITION.md` - readable hole card held by robot hand.
- `TURN_DETECTION.md` - physical turn button and `is_my_turn`.
- `COMMUNITY_CARDS.md` - shared board cards.
- `SHOWDOWN_OUTCOME.md` - showdown state, revealed cards, outcome.
- `CHIP_RECOGNITION.md` - remaining chip inventories.
- `BET_RECOGNITION.md` - current bet chips in each betting area.

Every captured-state parse has a baseline visual pass:

1. Check scene stability (current vs previous image) and turn detection.
2. Use baseline findings with caches and context to select additional visual
   questions for this iteration.
3. Run only the conditional guidelines needed for the expected stage.

Keep parsed state compact:

```json
{
  "loop_stage": "idle",
  "blind": "big_blind",
  "showdown_outcome": "not_showdown",
  "table": {
    "scene_stable": true,
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {"5": 4, "10": 3, "50": 3, "100": 3},
    "opponent_chips": {"5": 4, "10": 4, "50": 3, "100": 3},
    "my_current_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "opponent_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "uncertain_fields": []
  }
}
```

Do not store `null` or `"unknown"` for required fields. If evidence is
incomplete, inherit from previous state or caches; if none exist, fill the most
likely value and record in `uncertain_fields`.

## Poker Reasoning

When the router returns `choose_poker_action`, analyze the current parsed table,
hole-card cache, blind/dealer assignment, and action history. The blind amounts
are: small blind = 5, big blind = 10.

Return one recommended action: `check`, `fold`, `call`, `raise`, or `all_in`.
Validate the recommendation against parsed state and chip constraints, then
execute with `executor.py`.

## Actions

Supported action JSON:

```json
{"action": "wait", "reason": "scene_unstable", "sleep_seconds": 30}
{"action": "reset_to_init"}
{"action": "view_card", "position": "left"}
{"action": "show_card", "position": "left"}
{"action": "put_down_card", "position": "left", "face_up": false}
{"action": "check"}
{"action": "fold"}
{"action": "call"}
{"action": "raise", "amount": 80}
{"action": "all_in"}
{"action": "collect_winnings"}
{"action": "request_human", "reason": "dexterous hand is holding an unreadable card"}
{"action": "stop", "reason": "session ended"}
```

`reset_to_init` moves the dexterous hand to its true initial pose. Use this when
the robot's near-idle pose occludes the opponent's betting area or other table
regions. Capture a fresh image after reset before continuing visual parsing.

Run actions through `executor.py`:

```bash
python3 executor.py --action '{"action":"wait","reason":"not_my_turn","sleep_seconds":3}'
python3 executor.py --action '{"action":"view_card","position":"left"}'
python3 executor.py --action '{"action":"call"}'
python3 executor.py --continue-current
```

## Recovery

Use `to_recover` when a recent atom failed harmlessly and retry is safe.
Use `down` when continuation is unsafe. Request human help when a person must
fix the table:

```bash
python3 executor.py --action '{"action":"request_human","reason":"card was dropped"}'
```

## Core Workflow

After preflight, repeat this loop until the action is `stop`:

1. Capture or reuse the current state's image.
2. Run baseline visual parsing: scene stability and turn detection.
3. Run conditional visual questions based on expected stage.
4. Write `s_current/01_parsed_state.md` with JSON block.
5. Run `python3 router.py` and follow the gated route.
6. Execute actions with `executor.py`.
7. After `02_action.md` is written, create next state and capture:

```bash
python3 state.py begin-next --after sN
python3 capture.py --output s_current/00_capture.jpg
```

Then start the loop again from visual parsing.
