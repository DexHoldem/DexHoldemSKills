# DexHoldem V2 State Cache

DexHoldem V2 is designed for an agent such as Codex or Claude Code. The agent
does visual parsing and next-move decisions; scripts keep state durable and
recoverable.

## Experiment Layout

```text
experiments/
  current -> exp20260430_150000
  exp20260430_150000/
    pyproject.toml
    config.yaml
    utils.py
    capture.py
    state.py
    executor.py
    action_translator.py
    router.py
    remote_exec.py
    visual_guidelines/
    hole_card_cache.json
    action_sequence.json
    s0/
      00_capture.jpg
      01_parsed_state.md
      02_action.md
    s1/
      00_capture.jpg
    s_current -> s1
```

Preflight copies scripts and config into the experiment root for convenience.
The installed skill remains intact.

## State Folder Contract

Each `sN/` folder is filled in order:

1. `00_capture.jpg` - exact image used for visual analysis.
2. `01_parsed_state.md` - agent-authored parsed state.
3. `02_action.md` - committed action and execution result.

A new state folder is created only after `02_action.md` exists. Wait,
retryable recovery, and down recovery are real state transitions, so they also
get action files before the next state is created.

## Loop Stage

`loop_stage` describes the robot workflow after visual parsing is complete:

- `acting` - a robot atom action was dispatched recently or the hand is still
  moving; wait and reobserve.
- `atom_idle` - the hand has settled after an atom action, but the full action
  sequence still has pending steps.
- `idle` - the full action sequence finished cleanly and the dexterous hand is
  near initial pose with no large movement.
- `show_hand` - the opponent has shown hole cards or showdown has been reached;
  reveal the robot cards as needed and resolve the hand outcome.
- `win` - the opponent folded or the known showdown cards give the robot the
  stronger hand; pull back the recognized bet chips.
- `lose` - the robot folded or the known showdown cards give the opponent the
  stronger hand; do not pull chips back.
- `to_recover` - the previous atom action failed harmlessly or had no visible
  effect after the hand settled, and the table layout is safe enough to retry
  or repair from the cached action sequence.
- `down` - execution is failed, interrupted, blocked, or unsafe to continue
  blindly.

Visual parsing itself is not a durable loop stage. The agent writes the parsed
state after all vision calls needed for that state are finished.

## Parsed State

`01_parsed_state.md` should include prose and a compact JSON block. An `idle`
state needs the full table fields because poker reasoning and betting may
follow:

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
can be inferred later from the compact state and should not be stored in
`01_parsed_state.md`.

Run scene stability and turn detection for every captured-state parse and
include `table.scene_stable` plus `table.is_my_turn` even in non-idle states.
Those baseline findings are dependencies for the conditional visual guidelines
selected in the same iteration. Non-idle states do not need every other visual
field refreshed. For `acting`, `atom_idle`, `to_recover`, and `down`, keep the
parsed state focused on `loop_stage`, `robot`, scene stability, turn detection,
and any fields needed by the cached action sequence or recovery decision. For
`show_hand`, include community cards and visible showdown cards when available.
For `win`, include enough bet/chip counts to collect winnings.

## Hole Card Cache

Viewed hole cards are returned face-down. The image will no longer show the
card value, so the cache is authoritative. This file also stores the one-time
blind/dealer assignment recognized during preflight:

```json
{
  "schema_version": 1,
  "left": {
    "card": "Ah",
    "status": "cached",
    "source_state": "s3",
    "confidence": 0.9
  },
  "right": {
    "card": null,
    "status": "unknown",
    "source_state": null,
    "confidence": 0.0
  },
  "blinds": {
    "dealer": "robot",
    "small_blind": "robot",
    "big_blind": "opponent",
    "source_state": "s0",
    "status": "recognized"
  }
}
```

Cache a card only when the dexterous hand is holding a readable card during the
matching view-card sequence. Use the sequence intent to choose the exact slot;
do not infer the slot from the next empty field.

## Action Sequence Cache

Actions can span multiple individual robot policies and multiple state folders.
`action_sequence.json` is the authoritative progress record:

```json
{
  "schema_version": 1,
  "sequence_id": "seq_0003",
  "loop_stage": "atom_idle",
  "intent": "view_left_hole_card",
  "action": {"action": "view_card", "position": "left"},
  "plan": {
    "prefix": "reset",
    "commands": [
      "python Dexas-Policy/robot_client.py --instruction 0 --port 13579 --server_ip 192.168.1.200"
    ],
    "command_steps": ["pick_card"],
    "sequence_steps": ["pick_card", "read_card", "put_down_card", "verify_idle"]
  },
  "steps": [
    {"name": "pick_card", "status": "completed"},
    {"name": "read_card", "status": "completed"},
    {"name": "put_down_card", "status": "pending"},
    {"name": "verify_idle", "status": "pending"}
  ],
  "current_step": "put_down_card",
  "retry_count": 0,
  "last_error": null,
  "human_required": false,
  "safety_counters": {
    "consecutive_waits": 0,
    "total_waits": 0,
    "consecutive_recoveries": 0,
    "total_recoveries": 0,
    "executor_failures": 0,
    "action_sequences_started": 1
  }
}
```

For card viewing, use `acting` while the robot is moving and `atom_idle` after
an atom action settles but card-view steps remain. Use `idle` only after the
card is picked up, read, cached, returned face-down, and the dexterous hand is
visually near rest pose.
Use `to_recover` when a card-view atom failed harmlessly, such as the card not
being picked up and remaining near its original face-down position. Use `down`
instead if the card is dropped, exposed, misplaced, covered, or unsafe to retry.
The `plan` object is the translator output captured at action start. Do not
recompute it from a later state while retrying or verifying the same sequence.
The `safety_counters` object is experiment-level loop protection. It persists
across state folders and action sequence replacement, so repeated wait/recovery
cycles eventually route to `request_human` instead of looping forever.
After human inspection, use `state.py reset-safety --scope consecutive` only
when the human explicitly approves another wait/recovery attempt. Use
`--scope all` only when the human intentionally clears total wait or total
recovery caps for the session.

Step status meanings:

- `pending` - the atom has not been dispatched.
- `dispatched` - `executor.py` sent the robot policy for this atom, and the
  next capture must verify the physical result.
- `completed` - the atom result has been visually verified in `atom_idle`.

Do not mark a robot atom `completed` from the same state that dispatched it.
Complete it only after the next state image confirms the intended physical
effect.

For chip actions, the translator creates one step per moved chip and then a
visual-idle verification step. A `call` is computed from the current table as
`sum(opponent_bet) - sum(my_current_bet)`. A `raise` uses `amount` as the
target total bet after the raise, so pushed chips are
`amount - sum(my_current_bet)`.
For `call` and `raise`, the translator only emits exact chip combinations from
available `my_chips`. If exact chips are unavailable, it fails before robot
dispatch instead of overpaying with a larger chip.
Use `to_recover` when a chip push failed harmlessly, such as the target chip not
moving or not following the dexterous hand, and the unfolded chip/card layout
remains countable and undisturbed. Use `down` instead if chips are scattered,
mixed, hidden, or any non-target object moved.

After a confirmed `win`, `collect_winnings` pulls back chips from the recognized
bet areas. By default the translator keeps source zones separate:
`opponent_bet` and `my_current_bet`. The action sequence records
`source_zones` so recovery can tell which betting area a pull step targeted.
Use an explicit `chip_counts` override only when the visual parse gives a
clearer count of the chips to collect and zone information is not reliable.

```json
{
  "schema_version": 1,
  "sequence_id": "seq_0004",
  "loop_stage": "atom_idle",
  "intent": "call",
  "action": {"action": "call"},
  "plan": {
    "prefix": "reset",
    "commands": [
      "python Dexas-Policy/robot_client.py --instruction 3 --port 13579 --server_ip 192.168.1.200",
      "python Dexas-Policy/robot_client.py --instruction 2 --port 13579 --server_ip 192.168.1.200"
    ],
    "command_steps": ["push_chip_10_1", "push_chip_5_1"],
    "sequence_steps": ["push_chip_10_1", "push_chip_5_1", "verify_idle"],
    "chip_counts": {"5": 1, "10": 1},
    "computed": {
      "source": "opponent_bet_minus_my_current_bet",
      "my_current_bet_total": 10,
      "opponent_bet_total": 25,
      "physical_bet_chips": 15
    }
  },
  "steps": [
    {"name": "push_chip_10_1", "status": "completed"},
    {"name": "push_chip_5_1", "status": "pending"},
    {"name": "verify_idle", "status": "pending"}
  ],
  "current_step": "push_chip_5_1",
  "retry_count": 0,
  "last_error": null,
  "human_required": false
}
```

```json
{
  "schema_version": 1,
  "sequence_id": "seq_0005",
  "loop_stage": "atom_idle",
  "intent": "collect_winnings",
  "action": {"action": "collect_winnings"},
  "plan": {
    "prefix": "reset",
    "commands": [
      "python Dexas-Policy/robot_client.py --instruction 7 --port 13579 --server_ip 192.168.1.200",
      "python Dexas-Policy/robot_client.py --instruction 6 --port 13579 --server_ip 192.168.1.200"
    ],
    "command_steps": ["pull_chip_10_1", "pull_chip_5_1"],
    "sequence_steps": ["pull_chip_10_1", "pull_chip_5_1", "verify_idle"],
    "chip_counts": {"5": 1, "10": 1},
    "computed": {
      "source": "my_current_bet_plus_opponent_bet",
      "my_current_bet_total": 10,
      "opponent_bet_total": 5,
      "physical_collect_chips": 15
    }
  },
  "steps": [
    {"name": "pull_chip_10_1", "status": "completed"},
    {"name": "pull_chip_5_1", "status": "pending"},
    {"name": "verify_idle", "status": "pending"}
  ],
  "current_step": "pull_chip_5_1",
  "retry_count": 0,
  "last_error": null,
  "human_required": false
}
```

## Action File

`02_action.md` records the action chosen for the current state:

```json
{
  "action": "wait",
  "reason": "not_my_turn",
  "sleep_seconds": 30
}
```

or:

```json
{
  "action": "request_human",
  "reason": "Dexterous hand is holding an unreadable card.",
  "resume_options": ["mark_card", "confirm_card_returned", "abort_hand"]
}
```

## Agent Next-Move Priority

1. If `00_capture.jpg` is missing, capture it.
2. If `01_parsed_state.md` is missing, first run the every-iteration visual
   baseline: scene stability and turn detection. Use those baseline findings
   to select the other visual guidelines needed for the expected state, and
   include the baseline findings in each conditional visual prompt.
3. If `loop_stage` is `down`, inspect caches and recent states; choose wait or
   human help. Retry only after the state is reclassified as `to_recover`.
4. If the scene is unstable, write a `wait` action unless safety counters have
   reached their configured limit.
5. If `loop_stage` is `to_recover`, use the cached sequence plan to retry or
   repair the current embodied action after the scene is stable, unless retry
   safety counters have reached their configured limit.
6. If `loop_stage` is `acting`, write a short wait action and capture again.
7. If `loop_stage` is `show_hand`, reveal robot cards as needed, then resolve
   the showdown outcome.
8. If `loop_stage` is `win`, run `collect_winnings` after chip counts are
   clear.
9. If `loop_stage` is `lose`, do not pull chips back; wait, request human help,
   run `state.py next-hand`, or stop.
10. If `loop_stage` is `atom_idle`, continue or verify the current action
   sequence. Do not start unrelated poker reasoning.
11. If a readable held card appears during a view-card sequence, cache it.
12. If a cached viewed card has not been returned, continue `put_down_card`.
13. Mark `idle` only after the sequence is complete and the dexterous hand is
   near initial pose.
14. If it is not our turn, write a `wait` action.
15. If idle and hole cards are incomplete, start the next `view_card` sequence.
16. If idle, hole cards are known, scene is stable, and it is our turn, reason
    and execute the poker action.
17. For `call`, use the current `my_current_bet` and `opponent_bet`; do not
    add a separate `to_call` field.
18. Write `02_action.md` before `state.py begin-next`.

After a hand is over and the table is ready for the next hand, run
`state.py next-hand` before creating the next state. This clears hole cards and
resets `action_sequence.json` while preserving blind/dealer cache. Run
`state.py next-hand --refresh-blinds` instead when the dealer/small-blind button
may have moved.

## Useful Commands

```bash
python3 router.py
python3 state.py current
python3 state.py save-capture --source /tmp/frame.jpg
python3 state.py save-parsed --source parsed.md
python3 state.py save-action --source action.md
python3 state.py begin-next --after s0
python3 state.py cache-card --slot left --card Ah --source-state s3 --confidence 0.9
python3 state.py set-blinds --dealer robot --small-blind robot --big-blind opponent --source-state s0
python3 state.py prepare-retry --step push_chip_10_1 --reason to_recover
python3 state.py reset-safety --scope consecutive
python3 state.py next-hand
python3 state.py next-hand --refresh-blinds
python3 action_translator.py --action '{"action":"view_card","position":"left"}' --as-sequence-cache
python3 action_translator.py --action '{"action":"collect_winnings"}' --table '{"my_current_bet":{"5":1},"opponent_bet":{"10":1}}' --as-sequence-cache
python3 state.py start-action --sequence-json '<translator sequence-cache JSON>'
python3 state.py set-loop-stage --stage to_recover
python3 state.py set-loop-stage --stage show_hand
python3 state.py set-loop-stage --stage win
python3 state.py set-loop-stage --stage lose
python3 state.py set-loop-stage --stage atom_idle
python3 state.py set-loop-stage --stage acting
python3 state.py require-human --reason "Dexterous hand is holding an unreadable card" --resume-options mark_card,confirm_card_returned,abort_hand
```
