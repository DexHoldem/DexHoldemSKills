# DexHoldem Perception Eval Report

**Run ID:** p3_claude_split_batch010_claudebase_split_low  
**State:** s1  
**Image:** s1/00_capture.jpg  
**Visual Setting:** split (parallel subagents)  
**Date:** 2026-05-02  

---

## Visual Agent Results

All 9 visual subagents ran in parallel (wave 1) against `s1/00_capture.jpg`.

| Agent | Key Finding | Confidence |
|---|---|---|
| scene-stability | `scene_stable: true` — hand settled, no blur | 0.72 |
| turn-detection | `is_my_turn: true` — "Your Turn" button visible at robot seat | 0.95 |
| community-cards | `community_cards: []` — preflop, all center cards face-down | 0.82 |
| chip-recognition | `my_chips: 280`, `opponent_chips: 255` | 0.45 |
| bet-recognition | `my_current_bet: 40`, `opponent_bet: 15` | 0.35 |
| blind-button | `dealer: opponent`, `small_blind: opponent`, `big_blind: robot` | 0.88 |
| robot-behavior | `robot_holding_card: false` — hand near table but settled | 0.72 |
| showdown-outcome | `showdown_visible: false` — active hand, no showdown | 0.75 |
| held-card | `card_held: false` — no card face visible | 0.82 |

**Uncertain fields:** `my_chips`, `opponent_chips`, `my_current_bet`, `opponent_bet` (low confidence due to robot arm occlusion and camera angle).

---

## Parsed State Summary

- **loop_stage:** `acting` (from parsed state; consistent with action_sequence.json)
- **Current sequence step:** `pick_card` (status: dispatched)
- **scene_stable:** `true`
- **is_my_turn:** `true`
- **Street:** preflop, no community cards
- **Blinds:** robot = big blind, opponent = dealer + small blind
- **Robot arm:** visible, extended near table center-right, not holding a card

---

## Router Decision

**Route:** `wait`  
**Reason:** `robot_acting` — robot action sequence is in `acting` stage; scene is stable but the arm has not retracted, so the system waits for the motion to settle.

**Suggested action:**
```json
{
  "action": "wait",
  "reason": "robot_acting",
  "sleep_seconds": 3
}
```

**Next step:** Re-capture and re-parse after the wait. The `pick_card` step is dispatched; upon next parse the robot behavior agent should confirm whether the card has been picked up (transitioning toward `read_card`) or if recovery is needed.

---

## Router Judgment Trail

| Check | Result | Reason |
|---|---|---|
| capture_exists | true | 00_capture.jpg exists |
| parsed_state_exists | true | 01_parsed_state.md exists |
| parsed_state_valid | true | JSON has table object |
| action_sequence_valid | true | action_sequence.json loaded |
| hole_card_cache_valid | true | hole_card_cache.json loaded |
| loop_stage_source | parsed_state | loop_stage read from parsed state |
| loop_stage_valid | true | loop_stage is acting |
| table_required_fields | true | all required fields present |
| scene_stable | true | scene is stable |
| acting_sequence | wait | robot may still be moving or settling |

---

## Output Files

- `visual_raw/scene_stability.json`
- `visual_raw/turn_detection.json`
- `visual_raw/community_cards.json`
- `visual_raw/chip_recognition.json`
- `visual_raw/bet_recognition.json`
- `visual_raw/blind_button_recognition.json`
- `visual_raw/robot_behavior.json`
- `visual_raw/showdown_outcome.json`
- `visual_raw/held_card_recognition.json`
- `visual_summary.json`
- `eval_report.md`
- `s1/01_parsed_state.md` (written by harness)
