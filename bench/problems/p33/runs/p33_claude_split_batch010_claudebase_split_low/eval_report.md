# DexHoldem Perception Eval Report

**Problem ID:** p33  
**Run ID:** p33_claude_split_batch010_claudebase_split_low  
**Image:** s_current/00_capture.jpg  
**Date:** 2026-05-02  

---

## Router Decision

- **loop_stage:** `down` (from action_sequence.json)
- **Route:** `recover_down`
- **Agent required:** yes (`recover_down`)
- **Reasoning agent invoked:** no (loop_stage=down routes to recovery, not poker action selection)

---

## Visual Subagent Results (8 agents, run in parallel)

| Agent | Key Finding | Confidence |
|-------|-------------|------------|
| scene-stability | `scene_stable: true` — scene matches s30 exactly, no motion blur | 0.97 |
| turn-detection | `is_my_turn: true` — white "Your Turn" button visible at robot seat | 0.97 |
| blind-button-recognition | dealer=opponent, small_blind=opponent, big_blind=robot | 0.88 |
| showdown-outcome | `showdown_occurring: false` — all hole cards face-down | 0.82 |
| robot-behavior | `recovery_needed: true` — arm settled but stuck in lowered pose, not at rest | 0.72 |
| chip-recognition | my_chips≈55, opponent_chips≈45 (uncertain, occluded by arm) | 0.45 |
| bet-recognition | my_current_bet≈10, opponent_bet≈10 (uncertain, arm occlusion) | 0.45 |
| community-cards | 5 cards visible (river); reads [7h,6c,6s,6d,6h] but low confidence | 0.38 |

---

## Scene State Summary

- **Street:** River (5 community cards face-up)
- **Hole cards (cached):** left=9d, right=5d (both recognized in prior states s5, s15)
- **Blinds:** Robot=big blind, Opponent=dealer+small blind (consistent with hole_card_cache.json)
- **Turn:** Robot's turn (Your Turn button present)
- **Scene stable:** Yes

### Uncertain Fields

The following fields have low visual confidence and would be flagged as `uncertain_fields` in 01_parsed_state.md:
- `community_cards` (confidence 0.38 — arm occlusion, image angle)
- `my_chips`, `opponent_chips` (confidence 0.45 — arm occlusion)
- `my_current_bet`, `opponent_bet` (confidence 0.45 — arm occlusion)

---

## Robot Arm State

The robot arm is in a stalled mid-trajectory lowered pose over the right-center table area, consistent with the `down` loop_stage recorded in action_sequence.json. The arm has settled (no motion blur) but is not at rest/idle height. No card or chip appears to be gripped or pinned. The failed chip-push attempt left the arm in this position.

**action_sequence.json context:**
- `loop_stage: down`
- `human_required: true`
- `last_error: "The failed chip-push attempt is stuck mid-trajectory and requires manual reorganization."`

---

## Suggested Action

```json
{
  "action": "request_human",
  "reason": "loop_stage=down with human_required=true; robot arm stalled mid-trajectory in chip-push; manual reorganization required before any automatic retry",
  "resume_options": ["inspect_scene", "reset_consecutive_safety", "reset_all_safety", "abort_hand"]
}
```

The router's `recover_down` route requires an agent to inspect recent states and the cached sequence to choose retry, wait, or human help. Given that `human_required=true` is already set in action_sequence.json and the robot arm is visually confirmed in an unsafe non-rest pose over the table, **request_human is the correct action** — no automatic retry should proceed without human confirmation.

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
- `visual_summary.json`
- `eval_report.md`
