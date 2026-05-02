# DexHoldem Perception Eval Report

**Run ID:** p8_claude_split_batch010_claudebase_split_low  
**State:** s6  
**Date:** 2026-05-02  

---

## Pipeline Summary

### State Context

- **Sequence:** seq_view_left_hole_card (viewing left hole card)
- **Current step:** put_down_card (status: dispatched)
- **Loop stage in cache:** acting
- **Left hole card:** 9d (cached from s5)
- **Right hole card:** unknown (not yet cached)
- **Blinds:** dealer=opponent, small_blind=opponent, big_blind=robot

### Visual Parsing (s6)

Six visual subagents were launched in parallel on `s6/00_capture.jpg`:

| Agent | Key Finding |
|---|---|
| scene-stability-agent | `scene_stable=false` — robot arm mid-motion |
| turn-detection-agent | `is_my_turn=true` — "Your Turn" button on robot side |
| robot-behavior-agent | card still held, put_down_card in progress, safe |
| community-cards-agent | no community cards (preflop) |
| chip-recognition-agent | my_chips≈{5:4,10:4,50:3,100:3}, opponent≈{5:4,10:3,50:3,100:3} |
| bet-recognition-agent | my_bet≈{5:2,10:4,100:2}, opp_bet≈{10:3,100:3} |

### Routing Decision

The router evaluated the parsed state:
1. `loop_stage=acting` (from action_sequence.json)
2. `scene_stable=false`
3. Route: **wait** — robot is acting and scene is unstable; wait 3 seconds before re-parsing

No poker action reasoning was needed (state is not idle/ready-to-act).

### Action

```json
{"action": "wait", "reason": "robot_acting", "sleep_seconds": 3}
```

---

## Output Files

| File | Status |
|---|---|
| `visual_raw/scene_stability.json` | written |
| `visual_raw/turn_detection.json` | written |
| `visual_raw/robot_behavior.json` | written |
| `visual_raw/community_cards.json` | written |
| `visual_raw/chip_recognition.json` | written |
| `visual_raw/bet_recognition.json` | written |
| `visual_summary.json` | written |
| `s6/01_parsed_state.md` | written |
| `s6/02_action.md` | written |

---

## Notes

- Chip and bet counts are marked uncertain due to partial occlusion by the robot arm and camera body in s6.
- The put_down_card atom was dispatched in s5→s6 transition; the next state capture after the wait should show the arm returned to near-idle, which will allow the router to advance to `atom_idle` → `verify_dispatched_step_result`.
- Once the card is placed and verified, the right hole card (unknown) will need to be viewed before poker action selection.
