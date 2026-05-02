# DexHoldem Perception Eval Report

**Run ID:** `p6_claude_split_batch010_claudebase_split_low`  
**State evaluated:** `s4`  
**Image:** `s4/00_capture.jpg`  
**Date:** 2026-05-02

---

## Visual Subagents (all run in parallel, wave 1)

| Agent | Result | Confidence |
|---|---|---|
| scene-stability-agent | `scene_stable: false` — robot hand in active pick_card motion | 0.87 |
| turn-detection-agent | `is_my_turn: true` — Your Turn button at robot seat | 0.92 |
| robot-behavior-agent | `action_in_progress: true` — hand extended near hole-card zone, mid-grasp | — |
| community-cards-agent | `community_cards: []` — all 5 slots face-down, pre-flop | 0.92 |
| chip-recognition-agent | my: {5:4,10:3,50:2,100:4} / opp: {5:3,10:3,50:2,100:3} | 0.45 (uncertain) |
| bet-recognition-agent | my_bet: {5:2,10:2,50:0,100:0} / opp: {5:0,10:2,50:0,100:1} | 0.45 (uncertain) |
| held-card-recognition-agent | `card_visible: false` — pick_card in progress, no readable face | 0.85 |
| showdown-outcome-agent | `showdown_visible: false` — pre-flop, no face-up cards | — |
| blind-button-recognition-agent | dealer=opponent, small_blind=opponent, big_blind=robot | 0.85 |

---

## Parsed State Written

**File:** `s4/01_parsed_state.md`

- `loop_stage`: `acting`
- `scene_stable`: `false`
- `is_my_turn`: `true`
- `community_cards`: `[]`
- Chip and bet counts recorded with `uncertain_fields` flagged (chip/bet agents at 0.45 confidence due to robot arm occlusion and camera angle)

---

## Router Decision

**Route:** `wait`  
**Reason:** `scene_unstable`

Router path followed:
1. `capture_exists` ✓
2. `parsed_state_exists` ✓ (just written)
3. `parsed_state_valid` ✓
4. `action_sequence_valid` ✓ (`loop_stage=acting`, `current_step=pick_card` dispatched)
5. `loop_stage_valid` ✓ (`acting`)
6. `table_required_fields` ✓
7. `scene_stable = false` → **route_wait(scene_unstable)**

**Suggested action:**
```json
{"action": "wait", "reason": "scene_unstable", "sleep_seconds": 3}
```

**Reasoning agent:** Not invoked. No poker action selection is needed — the scene is unstable and the robot is mid-action on pick_card. Texas Hold'em strategy reasoning is only required once the scene is stable and it is the idle turn.

---

## Action Written

**File:** `s4/02_action.md`

Wait action recorded. Next step: re-capture after 3 seconds to check whether pick_card has completed and scene has stabilized.

---

## Output Files

| File | Status |
|---|---|
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_raw/scene_stability.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_raw/turn_detection.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_raw/robot_behavior.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_raw/community_cards.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_raw/chip_recognition.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_raw/bet_recognition.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_raw/held_card.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_raw/showdown_outcome.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_raw/blind_buttons.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/visual_summary.json` | ✓ written |
| `runs/p6_claude_split_batch010_claudebase_split_low/eval_report.md` | ✓ written |
| `s4/01_parsed_state.md` | ✓ written |
| `s4/02_action.md` | ✓ written |
