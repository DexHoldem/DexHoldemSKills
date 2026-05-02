# DexHoldem Perception Eval Report

**Run ID**: p21_claude_split_batch010_claudebase_split_low  
**State**: s18  
**Image**: s18/00_capture.jpg  

---

## Visual Perception

All 9 visual subagents were launched in a single parallel wave.

| Agent | Result |
|---|---|
| scene-stability-agent | scene_stable=true — robot idle, no motion, chip/card positions unchanged vs s17 |
| turn-detection-agent | is_my_turn=true — white "Your Turn" button visible in robot seat band |
| community-cards-agent | community_cards=[] — preflop, all 5 board slots face-down |
| chip-recognition-agent | my_chips≈45, opponent_chips≈40 (uncertain due to arm occlusion) |
| bet-recognition-agent | my_current_bet≈30, opponent_bet≈20 (uncertain due to overlap) |
| blind-button-recognition-agent | dealer=opponent, small_blind=opponent, big_blind=robot |
| robot-behavior-agent | hand_pose=idle/rest, action_in_progress=false, safety_ok=true |
| showdown-outcome-agent | showdown_in_progress=false, winner=unknown |
| held-card-recognition-agent | holding_card=false, held_card=null |

---

## State Assessment

**Loop stage**: `down` (from action_sequence.json — visual perception does not override this)

The action_sequence records:
- sequence_id: `seq_view_right_hole_card`
- current_step: `put_down_card` (status: failed)
- human_required: `true`
- last_error: `put_down_card_failed — right hole card put-down requires human help`

Visual evidence confirms the robot hand is in idle/rest pose and is not holding a card. Both hole cards are cached (left=9d, right=5d). Scene is stable. Despite the robot appearing idle, the explicit `human_required: true` flag in the sequence and the failed `put_down_card` step require human confirmation before automated recovery.

---

## Action Decision

**Action**: `request_human`

The sequence explicitly records `human_required: true` for a failed put_down_card operation. A human operator must inspect the physical table state — confirm where the right hole card is, verify it is correctly positioned face-down — before the sequence can be cleared or advanced.

```json
{
  "action": "request_human",
  "reason": "put_down_card step for right hole card failed with human_required=true; robot hand is visually idle but physical card placement must be confirmed by a human before the sequence can continue",
  "resume_options": ["inspect_scene", "reset_consecutive_safety", "reset_all_safety", "abort_hand"]
}
```

---

## Output Files

- `s18/01_parsed_state.md` — merged visual evidence + loop_stage from action_sequence
- `s18/02_action.md` — request_human action with reasoning
- `visual_raw/` — 9 raw evidence JSON files (one per visual subagent)
- `visual_summary.json` — merged summary of all visual findings and action
- `eval_report.md` — this file
