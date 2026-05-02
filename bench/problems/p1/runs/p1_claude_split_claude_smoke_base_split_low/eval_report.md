# Eval Report — p1_claude_split_claude_smoke_base_split_low

**State**: s0  
**Image**: s0/00_capture.jpg  
**Visual setting**: split/claude (9 parallel subagents)  
**Date**: 2026-05-02

---

## Visual Subagent Results

| Agent | Key Finding | Confidence |
|---|---|---|
| scene-stability-agent | scene_stable=true | 0.82 |
| turn-detection-agent | is_my_turn=true ("Your Turn" button on robot side) | 0.95 |
| community-cards-agent | community_cards=[], street=preflop | 0.85 |
| chip-recognition-agent | my_chips=18, opponent_chips=13 (value ~495 vs ~225) | 0.45 |
| bet-recognition-agent | my_current_bet=40, opponent_bet=15 | 0.45 |
| blind-button-recognition-agent | dealer=opponent, small_blind=opponent, big_blind=robot | 0.88 |
| robot-behavior-agent | robot_idle=true, robot_holding_card=false | 0.82 |
| showdown-outcome-agent | showdown_detected=false, winner=null | 0.82 |
| held-card-recognition-agent | holding_card=false, card=null | 0.92 |

All 9 agents ran in parallel (wave 1). No second wave required.

---

## Router Decision

Router path through `router.py`:

1. `capture_exists` → True
2. `parsed_state_exists` → True (written by this perception step)
3. `action_file_exists` → False (s0/02_action.md not present)
4. `parsed_state_valid` → True (table object present with required fields)
5. `action_sequence_valid` → True (loop_stage=idle)
6. `hole_card_cache_valid` → True (loaded; both slots status=unknown)
7. `loop_stage_valid` → True (idle)
8. `table_required_fields` → True (all idle-required fields present)
9. `scene_stable` → True
10. `is_my_turn` → True
11. `next_unknown_hole` → "left" (both hole card slots uncached)

**Route**: `view_hole_card`  
**Reason**: Left hole card is not cached — robot must view left card before poker action selection.  
**Suggested action**: `{"action": "view_card", "position": "left"}`  
**agent_required**: false  

> Robot action not executed per task instructions.

---

## Reasoning Agent

Not invoked. The router did not reach `choose_poker_action` because hole cards are not yet cached.  
The reasoning agent will be needed once both hole cards (left and right) are cached and the router reaches the `choose_poker_action` route in a subsequent state.

---

## Uncertain Fields

The following fields have low confidence (0.45) due to camera angle, perspective distortion,
and partial occlusion of the right chip group by the robot arm:

- `my_chips` — robot arm occludes right chip group
- `opponent_chips` — far-side perspective distortion
- `my_current_bet` — chip overlap in betting zone
- `opponent_bet` — partial occlusion near BIG BLIND button

These would be resolved via `resolve_uncertain_fields` if the router reached that point, but
since hole cards take priority, they will be re-evaluated after the view_card sequence.

---

## Output Files

| File | Status |
|---|---|
| runs/p1_claude_split_claude_smoke_base_split_low/visual_raw/scene_stability.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/visual_raw/turn_detection.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/visual_raw/community_cards.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/visual_raw/chip_recognition.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/visual_raw/bet_recognition.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/visual_raw/blind_button_recognition.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/visual_raw/robot_behavior.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/visual_raw/showdown_outcome.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/visual_raw/held_card_recognition.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/visual_summary.json | written |
| runs/p1_claude_split_claude_smoke_base_split_low/eval_report.md | written |
| s0/01_parsed_state.md | written |
