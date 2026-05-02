# DexHoldem Perception Eval Report

**Run ID:** p19_claude_split_batch010_claudebase_split_low  
**State:** s18  
**Date:** 2026-05-02

---

## Visual Perception Results

8 visual subagents ran in parallel on `s18/00_capture.jpg`.

| Agent | Finding |
|---|---|
| scene-stability | **Stable** — robot at rest, no motion blur, chip/card positions consistent vs s17 |
| turn-detection | **Robot's turn** — "Your Turn" button visible at robot seat |
| community-cards | **None** — preflop, no face-up cards on board |
| chip-recognition | my_chips=160, opponent_chips=295 (uncertain due to distance/overlap) |
| bet-recognition | my_current_bet=30, opponent_bet=15 (opponent side partially occluded) |
| robot-behavior | **Not holding card**, not mid-action, at rest/idle pose |
| blind-button | dealer=opponent, small_blind=opponent, big_blind=robot |
| showdown-outcome | No showdown detected, hand still in progress |

---

## Action Sequence Context

- **loop_stage:** `down`
- **intent:** `view_right_hole_card`
- **current_step:** `put_down_card` (status: failed)
- **human_required:** true
- **last_error:** `put_down_card_failed — right hole card put-down requires human help`
- **Hole cards cached:** left=9d, right=5d (both recognized)

---

## Router Decision

**Route:** `recover_down`  
**Agent required:** Yes (`recover_down` task)

**Reasoning:**
- `loop_stage` is `down` (from action_sequence.json, confirmed in parsed state)
- `human_required=true` is set in the action sequence
- Visual evidence: robot is **not holding any card** and is in idle pose in s18
- The prior `put_down_card` failure set human_required; however visually the robot appears to have released the card already
- Scene is stable and it is the robot's turn

**Recovery Assessment:**
The visual evidence suggests the physical state may have self-resolved (robot not holding card in s18), but the action sequence flags `human_required=true`. Safe next step is `request_human` to:
1. Confirm the right hole card (5d) is back on the table face-down at the correct position
2. Confirm the robot arm is clear and safe to resume
3. Resume with `reset_consecutive_safety` and transition to `idle` loop stage

**No poker action was taken.** Execution is blocked pending human confirmation per `human_required=true`.

---

## Output Files

- `visual_raw/scene_stability.json`
- `visual_raw/turn_detection.json`
- `visual_raw/community_cards.json`
- `visual_raw/chip_recognition.json`
- `visual_raw/bet_recognition.json`
- `visual_raw/robot_behavior.json`
- `visual_raw/blind_button.json`
- `visual_raw/showdown_outcome.json`
- `visual_summary.json`
- `s18/01_parsed_state.md` (written to experiment directory)
