# DexHoldem Perception Eval Report

**Run ID:** p11_claude_split_batch010_claudebase_split_low  
**State:** s3  
**Image:** s3/00_capture.jpg  
**Date:** 2026-05-02

---

## Visual Agents (Parallel Wave 1)

All 8 visual subagents ran in parallel on `s3/00_capture.jpg`.

| Agent | Result | Notes |
|---|---|---|
| scene-stability-agent | scene_stable: **true** | Robot arm settled in new rest pose; cards/chips consistent between s2 and s3 |
| turn-detection-agent | is_my_turn: **true** | White "Your Turn" button visible at robot seat |
| community-cards-agent | community_cards: **[]** | No face-up community cards; preflop state |
| chip-recognition-agent | my_chips: ~480, opponent_chips: ~355 | Uncertain — partial occlusion by robot arm |
| bet-recognition-agent | my_current_bet: ~20, opponent_bet: ~10 | Uncertain — partial occlusion by robot arm |
| blind-button-recognition-agent | dealer/SB: opponent, BB: robot | Consistent with hole_card_cache.json cached blinds |
| robot-behavior-agent | robot_idle: true, card on table, recovery_possible: true | Card dropped but fell back face-down; no displacement |
| showdown-outcome-agent | showdown_active: false | All cards face-down; no showdown in progress |

---

## Routing

**Loop stage in action_sequence.json:** `down`  
**Loop stage in parsed state (01_parsed_state.md):** `down`  
**Router route:** `recover_down`

The router dispatches to `recover_down` because `loop_stage == "down"` in the parsed state. This requires agent judgment on whether to retry, wait, or escalate to human.

---

## Recovery Assessment

The action_sequence.json records:
- `last_error`: `{code: "card_dropped", message: "left hole card dropped during pickup"}`
- `human_required`: `true`
- `current_step`: `pick_card` (status: failed)
- Left hole card NOT yet cached (hole_card_cache: `{left: {card: "9d", status: "recognized", source_state: "s5"}}` — note: source_state s5 is future state, left card is actually unknown in current context; right: unknown)

**Robot-behavior agent findings:**
- Dexterous hand is retracted and at rest — not holding any object
- Both hole cards appear face-down in their expected positions
- No face-up exposure, no card scattered outside the zone
- The drop was likely a missed pickup (card slipped back to table) rather than a damaging scatter

**Safety ruling:**  
Despite visual evidence suggesting a safe retry may be possible, the `human_required: true` flag in the action_sequence is a hard safety constraint. It must be cleared by a human operator before autonomous retry is permitted.

---

## Reasoning Agent

Not invoked. The route is `recover_down` (physical recovery, not a poker decision). No Texas Hold'em action selection was required.

---

## Decided Action

```json
{
  "action": "request_human",
  "reason": "action_sequence.json has human_required=true after card_dropped on pick_card (left hole card). Visual inspection shows the card is face-down in position and the robot arm is idle — a retry may be safe — but human_required must be cleared by a human before autonomous retry is permitted.",
  "resume_options": ["inspect_scene", "reset_consecutive_safety", "reset_all_safety", "abort_hand"]
}
```

---

## Output Files

| File | Status |
|---|---|
| `visual_raw/scene_stability.json` | written |
| `visual_raw/turn_detection.json` | written |
| `visual_raw/community_cards.json` | written |
| `visual_raw/chip_recognition.json` | written |
| `visual_raw/bet_recognition.json` | written |
| `visual_raw/blind_button.json` | written |
| `visual_raw/robot_behavior.json` | written |
| `visual_raw/showdown_outcome.json` | written |
| `visual_summary.json` | written |
| `eval_report.md` | written |
| `s3/01_parsed_state.md` | written |
| `s3/02_action.md` | written |
