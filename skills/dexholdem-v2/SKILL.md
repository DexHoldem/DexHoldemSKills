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

The main agent owns final state interpretation. Helpers may mutate caches,
action metadata, and state files only when the main agent invokes them.
Visual subagents never write state files; they only return evidence for the
main agent to merge.

The workflow is state-folder based. Every decision is grounded in the current
state image, parsed state markdown, local caches, and the current action
sequence.

## Session Start

First, from the user's working directory, expose the helper scripts at the
workspace root:

```bash
ln -s .agents/skills/dexholdem-v2/scripts/*.py ./
```

For Claude installations, use the Claude skill path instead:

```bash
ln -s .claude/skills/dexholdem-v2/scripts/*.py ./
```

Then run preflight from the user's working directory:

```bash
python3 preflight.py
python3 preflight.py --exp-name my_run
```

On Ubuntu/Linux, preflight can install a local TTS backend for action
announcements:

```bash
python3 preflight.py --install-system-packages
```

This uses `apt-get` and non-interactive `sudo`; run `sudo -v` first or run
preflight as root if the machine requires a sudo password.

For a hardware-free smoke check:

```bash
python3 preflight.py --skip-camera --skip-remote --skip-audio
```

Pause after preflight. Inspect the printed result, confirm the experiment
directory exists, confirm `s0/00_capture.jpg` exists when camera was not
skipped, and report any preflight error or suspicious setup instead of
continuing the workflow automatically.

Preflight creates `experiments/<exp-name>/`, points `experiments/current` to
that folder, initializes `s0/` and `s_current`, copies the executable helper
scripts plus `pyproject.toml` and `config.yaml` into the experiment root, and
validates remote click coordinates before capturing `s0/00_capture.jpg` unless
camera checks are skipped.

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

Blind amounts are fixed for this setup: the small blind is an initial bet of 5
chips, and the big blind is an initial bet of 10 chips. Use the cached
small-blind/big-blind assignment with visible bet recognition when reasoning
about preflop current bets.

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

The normal exceptions are `stop`, which ends the session instead of continuing
the timeline, and `request_human`, which blocks automatic state advance until a
human confirms how to proceed.

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

Step status is deliberately physical:

- `pending` means the atom has not been dispatched.
- `dispatched` means `executor.py` sent the robot policy, but the next capture
  has not yet verified the physical result.
- `completed` means the atom was visually verified in an `atom_idle` state.

`executor.py` dispatches at most one robot atom command per state. It marks the
step `dispatched`; the main agent marks it `completed` only after visual
verification.

Useful cache helpers:

```bash
python3 state.py cache-card --slot left --card Ah --source-state s3 --confidence 0.9
python3 action_translator.py --action '{"action":"view_card","position":"left"}' --as-sequence-cache
python3 state.py start-action --sequence-json '<translator sequence-cache JSON>'
python3 state.py dispatch-step --step pick_card
python3 state.py complete-step --step read_card
python3 state.py prepare-retry --step push_chip_10_1 --reason to_recover
python3 state.py next-hand
python3 state.py next-hand --refresh-blinds
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

Use the files in `visual_guidelines/` as needed to write a truthful
`loop_stage`, `robot`, and table fields. Multiple visual checks may be used for
the same captured state when they add useful information. The visual model may
answer in plain language; the coding agent converts those answers into
`01_parsed_state.md`.

When visual information is needed, the main agent MUST delegate image reading
to visual subagents. Assign each subagent one guideline or one visual question,
such as scene stability, robot behavior, turn button, community cards, bets,
chip inventory, held card reading, or showdown outcome. Give each subagent the
current image, relevant recent images, cache summaries, action-sequence context,
and the appropriate visual guideline as its prompt. Subagents are read-only
evidence providers: they must inspect images and context, return findings,
evidence, uncertainty, and suggested parsed fields, but must not edit state
files. The main agent merges the subagent outputs, resolves conflicts
conservatively, and writes the single authoritative
`s_current/01_parsed_state.md`.

Guideline purposes:

- `SCENE_STABILITY.md` - action completion, waiting decisions, and movement
  checks, usually paired with recent images.
- `ROBOT_BEHAVIOR.md` - dexterous-hand pose, motion, held objects, physical
  safety, atom progress, and recovery context. A robot-behavior subagent should
  receive at least the current image and the previous captured image so it can
  judge motion, progress, and whether the hand has actually settled.
- `TABLE_GEOMETRY.md` - robot/opponent orientation, betting zones, inventory
  zones, and camera/table layout.
- `BLIND_BUTTON_RECOGNITION.md` - dealer, small blind, and big blind buttons.
- `HELD_CARD_RECOGNITION.md` - readable hole card held by the robot hand.
- `TURN_DETECTION.md` - physical white turn button and `is_my_turn`.
- `COMMUNITY_CARDS.md` - shared board cards.
- `SHOWDOWN_OUTCOME.md` - showdown state, revealed cards, fold/win/lose
  outcome.
- `CHIP_RECOGNITION.md` - remaining chip inventories.
- `BET_RECOGNITION.md` - current bet chips in each betting area.

It is acceptable to refresh `is_my_turn`, board, chips, bets, and robot state
on every captured image if that helps keep the parsed state current. The router
will decide which fields matter for the current `loop_stage`.

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
table block shown above. Non-idle states must still include a `table` object,
but it may be sparse when fields were not visually parsed and are irrelevant to
the current gate. Include `uncertain_fields` when an omitted or unclear value
matters to the next action.

For showdown, use `loop_stage` as the main compact signal. Add only small table
notes that help routing or verification, such as visible opponent hole cards;
do not store bulky hand-ranking explanations.

## Poker Reasoning

When the router returns `choose_poker_action`, the main agent MUST delegate the
Texas Hold'em reasoning to a reasoning subagent. Give the subagent the current
parsed table, hole-card cache, blind/dealer assignment, action history if
available, supported action space, and the blind amounts: small blind = 5,
big blind = 10.

The reasoning subagent should infer the current betting situation from
`my_current_bet`, `opponent_bet`, `my_chips`, `opponent_chips`, community
cards, hole cards, turn state, and blind assignment. It should return a concise
rationale plus one recommended supported action JSON, such as `check`, `fold`,
`call`, `raise`, or `all_in`. The main agent validates that recommendation
against the current parsed state, supported action schema, and physical chip
constraints, then commits and executes the final action through `executor.py`.

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

For `call` and `raise`, chip selection must be exact. If available `my_chips`
cannot form the required amount exactly, the translator fails before robot
dispatch. Do not silently overpay with a larger chip; choose a different poker
action, repair chip recognition, or request human help.

Chip actions are translated into one atom step per moved chip, such as
`push_chip_10_1` and `push_chip_5_1`, followed by `verify_idle`.

`check` has no robot motion. Its translation includes a `text_to_sound` payload,
and the executor runs `text_to_sound.py` to announce "Check" before completing
the action as `idle`. With `text_to_sound.backend: auto`, macOS uses
`say` plus `afplay`; Ubuntu/Linux uses the first available local backend among
`spd-say`, `espeak-ng`, and `espeak`.

`request_human` also includes a `text_to_sound` payload. The executor speaks
the action `reason` directly, then marks the sequence `down` through
`state.py require-human`. Use `speech_text` only when the spoken wording should
differ from the logged reason.

`collect_winnings` pulls chips back after a confirmed `win`. By default it
pulls `opponent_bet` and `my_current_bet` as separate source zones from the
parsed table, then records those zones in the action sequence. Use `chip_counts`
only when visual parsing has a clearer explicit count for the chips that should
be pulled back and zone information is not reliable.

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
python3 executor.py --action '{"action":"request_human","reason":"Dexterous hand is holding an unreadable card","resume_options":["mark_card","confirm_card_returned","abort_hand"]}'
```

`request_human` is a blocking action. After it writes `02_action.md`, the router
returns `human_pause` and does not automatically create the next state. Only
after a human confirms the table is fixed should the agent run the router's
`commands_after_human` to create and capture the next state.

Retry only when the cached sequence plan and recent images show that repeating
the current step is physically safe. In normal routing, that means the parsed
state should be `to_recover`; otherwise keep the state `down` and request human
help or wait for clearer evidence. For retryable atom failures, use
`state.py prepare-retry --step <current_step>` followed by
`executor.py --continue-current`; the router emits these commands when the
current step has a cached atom command. Safety counters in
`action_sequence.json` cap repeated waits and recoveries; when a cap is reached,
the router escalates to `request_human` instead of continuing automatically.
If a human inspects the table and explicitly approves continuing, run
`state.py reset-safety --scope consecutive` before creating the next captured
state. Use `--scope all` only when the human intentionally clears total wait or
total recovery caps for the session.

After a hand ends, either stop the session or reset local caches before the next
hand. Use `state.py next-hand` to clear hole cards and reset
`action_sequence.json` while preserving blind/dealer cache. Use
`state.py next-hand --refresh-blinds` when the dealer/small-blind button may
have moved and blind recognition must run again during the next preflight-like
visual pass.

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
   - If it asks to verify a dispatched step, inspect the current image and
     cached sequence. If the intended atom succeeded, run the provided
     `state.py complete-step ...` command and rerun the router. If it failed
     harmlessly, mark `to_recover`; if unsafe, mark `down` or request human
     help.
   - If it asks for held-card reading, use visual parsing to read the held card,
     update `hole_card_cache.json`, and continue the cached action sequence.
   - If it returns `continue_cached_command`, run `executor.py
     --continue-current`; this sends the next pending robot atom from
     `action_sequence.json`.
   - If it returns `recover_retryable` with commands, run them in order to reset
     and retry the exact cached atom. If it requires the agent, inspect the
     cached sequence and recent images before retrying or requesting help.
   - If it returns `recover_down`, inspect recent states and choose wait or
     `request_human`; only retry after the state is safely classified as
     `to_recover`.
   - If it returns `human_pause`, wait for human confirmation before running the
     supplied `commands_after_human`.
   - If it returns `show_hand`, reveal robot cards as needed with `show_card`
     actions, then use `SHOWDOWN_OUTCOME.md` to decide `win`, `lose`, or keep
     resolving showdown ambiguity.
   - If it returns `collect_winnings`, execute the suggested
     `collect_winnings` action with `executor.py`.
   - If it returns `hand_lost`, do not move chips toward the robot; decide
     whether to wait for reset, request human help, run `state.py next-hand`,
     or stop.
   - If it returns `choose_poker_action`, delegate Texas Hold'em reasoning to a
     reasoning subagent with the parsed table state, hole-card cache,
     blind/dealer assignment, action history, supported action space, and blind
     amounts. Validate the subagent's recommended action, use
     `action_translator.py` if you need to inspect the new action sequence, and
     execute the final action with `executor.py`.
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
python3 executor.py --continue-current
python3 executor.py --action '{"action":"call"}'
python3 executor.py --action '{"action":"collect_winnings"}'
python3 executor.py --action '{"action":"request_human","reason":"card was dropped"}'
```

After `executor.py` writes `02_action.md`, create the next state and capture the
next observation unless the route is `human_pause` or the action is `stop`:

```bash
python3 state.py current
python3 state.py begin-next --after sN
python3 capture.py --output s_current/00_capture.jpg
```

Then start the loop again from visual parsing. The next image verifies what
actually happened after the last wait, retry, robot action, or human-help
request.
