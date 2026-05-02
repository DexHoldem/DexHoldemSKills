# DexHoldem Perception Eval Report

**Run ID:** p14_claude_split_batch010_claudebase_split_low  
**State:** s9  
**Image:** s9/00_capture.jpg  
**Date:** 2026-05-02

---

## Visual Subagent Results (8 agents, parallel wave)

| Agent | Result | Confidence |
|---|---|---|
| scene-stability | `scene_stable: true` | High — s8/s9 frames visually identical |
| turn-detection | `is_my_turn: true` | High — "Your Turn" button clearly visible |
| community-cards | `community_cards: []`, street: preflop | High — no face-up cards in board area |
| chip-recognition | `my_chips: 470`, `opponent_chips: 400` | Medium — robot arm occludes some chips |
| bet-recognition | `my_current_bet: 30`, `opponent_bet: 10` | Medium — robot arm partially occludes right bet zone |
| blind-button | dealer: opponent, SB: opponent, BB: robot | High — yellow BB button at robot seat confirmed |
| robot-behavior | `robot_idle: false`, `safety_ok: true` | Medium — hand deployed but scene confirmed stable |
| showdown-outcome | `showdown_active: false` | High — all cards face-down, no muck/fold visible |

---

## Merged Parsed State

- **Loop stage:** idle (prior sequence `seq_view_left_hole_card` fully complete)
- **Scene stable:** true
- **Robot's turn:** true
- **Street:** preflop — no community cards
- **Blinds:** opponent=dealer/SB, robot=BB
- **Robot chips:** ~470 | **Opponent chips:** ~400
- **Robot bet:** ~30 | **Opponent bet:** ~10

---

## Hole Card Cache Status

| Slot | Card | Status |
|---|---|---|
| Left | 9♦ (9d) | recognized (s5) |
| Right | — | **unknown** |

---

## Router Decision

**Route:** `view_hole_card`  
**Reason:** Right hole card is not cached. Robot must view and cache the right hole card before poker action selection can proceed.

**Suggested action:**
```json
{"action": "view_card", "position": "right"}
```

**Agent required:** No  
**Robot action required:** Yes (view right card) — **not executed per instructions**

---

## Notes

- Robot behavior agent noted the hand is not at full rest pose; however, scene-stability agent confirmed s8 and s9 are visually identical with the hand in a settled position. The scene is treated as stable.
- Chip and bet counts carry medium confidence due to partial occlusion by the robot arm in the right side of the frame.
- Router logic was traced manually; shell execution of `router.py` was not permitted.

---

## Output Files

| File | Status |
|---|---|
| `visual_raw/scene_stability.json` | ✓ written |
| `visual_raw/turn_detection.json` | ✓ written |
| `visual_raw/community_cards.json` | ✓ written |
| `visual_raw/chip_recognition.json` | ✓ written |
| `visual_raw/bet_recognition.json` | ✓ written |
| `visual_raw/blind_button_recognition.json` | ✓ written |
| `visual_raw/robot_behavior.json` | ✓ written |
| `visual_raw/showdown_outcome.json` | ✓ written |
| `visual_summary.json` | ✓ written |
| `eval_report.md` | ✓ written |
| `s9/01_parsed_state.md` | ✓ written |
