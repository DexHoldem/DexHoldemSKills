# DexHoldem Perception Eval Report

**Run ID:** p31_claude_split_batch010_claudebase_split_low  
**Problem ID:** p31  
**Step analyzed:** s30  
**Date:** 2026-05-02

---

## Visual Subagent Results (parallel wave)

| Agent | Result | Confidence |
|---|---|---|
| scene-stability | NOT stable | high |
| turn-detection | is_my_turn = true | high |
| community-cards | Obstructed; fallback to s29: Qh, 7d, 6s, Jc | low (s30) / high (s29) |
| chip-recognition | Both areas occluded; s29 values used | low (s30) |
| bet-recognition | Both areas partially occluded; s29 values used | low (s30) |
| robot-behavior | Hand visible, settled post-action, safety ok | medium |
| showdown-outcome | No showdown active | high |

---

## Scene Stability

The scene is **not stable**. The robot arm moved substantially between s29 and s30:
- In s29: arm retracted to the right side of the scene
- In s30: arm fully extended over the table, dexterous hand touching the felt near chip/card area

The arm has not yet returned to an idle position. This transition is consistent with the ongoing chip-push action (pushing 100-chip raise) recorded in the action sequence.

---

## Robot Behavior

The dexterous hand is visible and appears settled (no motion blur). Fingers rest on the felt near the robot's hole cards and chip stacks. The table layout (two face-down hole cards, chip groups, Your Turn marker, Big Blind button) appears intact. No scattered chips, no exposed cards, no safety violation observed.

The robot behavior agent assesses: action likely complete from a mechanical standpoint, but arm has not yet returned to idle.

---

## Game State

- **Street:** Turn (4 community cards)
- **Community cards:** Qh, 7d, 6s, Jc (from s29; s30 obstructed)
- **Robot hole cards:** 9d (left), 5d (right) — from cache, confirmed in s5/s15
- **Blind position:** Robot = Big Blind
- **Robot chips (s29):** 5×4, 10×3, 50×3, 100×3
- **Opponent chips (s29):** 5×2, 10×4, 50×3, 100×3
- **Robot current bet (s29):** 10×1, 50×1, 100×1 (total ~160)
- **Opponent current bet (s29):** 5×2, 50×1, 100×1 (total ~160)
- **Action in progress:** Robot was pushing 100-chip to raise; motion in progress since s29

---

## Poker Reasoning

**Not delegated to reasoning subagent.** No new poker decision is required at this step. The scene is not stable, the robot arm is mid-return from the chip-push action, and the current intent is `wait_for_motion_completion`. A poker decision was already made (raise) and its mechanical execution is completing.

---

## Recommended Action

**`wait`** — Continue waiting for the robot arm to return to idle and for the scene to stabilize before the next perception-action cycle. The chip push appears to have been executed; next stable capture should confirm the updated chip/bet state.

---

## Output Files

- `visual_raw/scene_stability.json`
- `visual_raw/turn_detection.json`
- `visual_raw/community_cards.json`
- `visual_raw/chip_recognition.json`
- `visual_raw/bet_recognition.json`
- `visual_raw/robot_behavior.json`
- `visual_raw/showdown_outcome.json`
- `visual_summary.json`
- `eval_report.md`
