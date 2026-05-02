# DexHoldem Perception Eval Report

**Run ID**: p13_claude_split_batch010_claudebase_split_low  
**State evaluated**: s7  
**Date**: 2026-05-02

---

## Router Decision

| Field | Value |
|---|---|
| Route | `recover_down` |
| Agent required | Yes (`recover_down`) |
| Loop stage | `down` |

**Reason**: `action_sequence.json` records `loop_stage=down`, `human_required=true`, and `current_step=put_down_card` (status: failed). The router's `down` branch requires agent judgment for recovery. Since `human_required=true` was already set, the correct next action is `request_human` — no automated retry should be attempted.

---

## Visual Parse Summary (s7)

| Check | Result |
|---|---|
| scene_stable | **false** — robot arm moved between s6→s7, not at rest pose |
| is_my_turn | true — "Your Turn" button visible |
| community_cards | [] (preflop, no cards dealt) |
| my_chips | ~340 (uncertain due to overlap) |
| opponent_chips | ~435 (uncertain due to overlap) |
| my_current_bet | ~25 (1 red + 2 blue chips left of community area) |
| opponent_bet | null (occluded by robot arm) |
| dealer | opponent |
| small_blind | opponent |
| big_blind | robot |
| showdown_in_progress | false |
| robot_pose | mid_action (hand near hole-card zone, not at rest) |
| action_in_progress | false (hand is settled, not moving) |
| safety_concern | true (card placement occluded, human_required=true) |

**Uncertain fields**: `my_chips`, `opponent_chips`, `my_current_bet`, `opponent_bet`

---

## Subagents Run (parallel wave)

All 8 visual subagents ran in a single parallel wave:

1. `scene-stability-agent` → scene_stable=false
2. `turn-detection-agent` → is_my_turn=true
3. `community-cards-agent` → [] preflop
4. `chip-recognition-agent` → my=340, opp=435
5. `bet-recognition-agent` → my_bet=25, opp_bet=null
6. `blind-button-recognition-agent` → dealer=opponent, bb=robot
7. `robot-behavior-agent` → mid_action, safety_concern=true
8. `showdown-outcome-agent` → no showdown

No poker action reasoning was requested (loop_stage=down, not idle).

---

## Action Recommendation

**Do not execute any robot action.**

The system is in `loop_stage=down` with `human_required=true`. The left hole card put-down failed and the robot hand is settled near the hole-card zone with the card placement occluded. Human inspection and intervention are required before any automated action can proceed.

Suggested action (for human review):
```json
{
  "action": "request_human",
  "reason": "put_down_card failed for left hole card; human_required=true; robot hand near hole-card zone with occluded card placement",
  "resume_options": ["inspect_scene", "reset_consecutive_safety", "reset_all_safety", "abort_hand"]
}
```

---

## Output Files

- `visual_raw/scene_stability.json`
- `visual_raw/turn_detection.json`
- `visual_raw/community_cards.json`
- `visual_raw/chip_recognition.json`
- `visual_raw/bet_recognition.json`
- `visual_raw/blind_button.json`
- `visual_raw/robot_behavior.json`
- `visual_raw/showdown_outcome.json`
- `visual_summary.json`
- `eval_report.md`
- `s7/01_parsed_state.md` (written to experiment directory)
