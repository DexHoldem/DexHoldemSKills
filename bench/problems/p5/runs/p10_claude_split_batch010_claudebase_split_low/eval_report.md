# DexHoldem Perception Eval Report

**Run ID**: `p10_claude_split_batch010_claudebase_split_low`  
**State**: `s3`  
**Date**: 2026-05-02  

---

## Situation Summary

The robot is in a **recovery loop** (`loop_stage: to_recover`). The previous action sequence (`view_left_hole_card`) had its `pick_card` step fail — the robot arm did not secure the left hole card. The card remains face-down at its original position. No damage was done to game state.

The hole card cache has:
- **Left**: `9d` (cached from s5, confidence 1.0)
- **Right**: unknown

---

## Visual Agent Results (9 agents, all parallel)

| Agent | Key Finding | Confidence |
|---|---|---|
| scene-stability-agent | scene_stable=**false** — robot arm moved between s2→s3 | 0.72 |
| turn-detection-agent | is_my_turn=**true** — "Your Turn" button visible | 0.85 |
| community-cards-agent | community_cards=**[]** — preflop, no board cards | 0.88 |
| chip-recognition-agent | my_chips≈**270**, opponent_chips≈**255** | 0.40 |
| bet-recognition-agent | my_bet≈**40**, opponent_bet≈**65** | 0.35 |
| blind-button-recognition-agent | dealer=opponent, SB=opponent, BB=**robot** | 0.75 |
| robot-behavior-agent | robot_idle=**true**, card_held=**false**, recovery_possible=**true** | 0.85 |
| showdown-outcome-agent | showdown_active=**false** | 0.72 |
| held-card-recognition-agent | card_held=**false** — pick genuinely failed | 0.85 |

---

## Router Decision

**Route**: `wait`  
**Reason**: `to_recover` loop stage + `scene_stable=false` → the router requires a stable scene before retrying the failed pick_card step. The robot arm changed position between s2 and s3, indicating it has not yet settled.

**Suggested action**:
```json
{"action": "wait", "reason": "to_recover_scene_unstable", "sleep_seconds": 3}
```

**Next expected route**: Once the scene stabilizes (robot arm at rest), the router will issue `recover_retryable` → retry `pick_card` for the left hole card.

---

## Reasoning Agent

Not invoked. The `wait` route does not require Texas Hold'em action reasoning — no poker decision is needed at this step.

---

## Safety Assessment

- No safety concerns detected
- pick_card failure was harmless (card unmoved, face-down)
- retry_count=0, max_step_retries=2 → 2 retries remaining
- total_recoveries=1, within safety limits
- Human intervention not required

---

## Output Files

| File | Status |
|---|---|
| `s3/01_parsed_state.md` | Written |
| `visual_raw/scene_stability.json` | Written |
| `visual_raw/turn_detection.json` | Written |
| `visual_raw/community_cards.json` | Written |
| `visual_raw/chip_recognition.json` | Written |
| `visual_raw/bet_recognition.json` | Written |
| `visual_raw/blind_button_recognition.json` | Written |
| `visual_raw/robot_behavior.json` | Written |
| `visual_raw/showdown_outcome.json` | Written |
| `visual_raw/held_card_recognition.json` | Written |
| `visual_summary.json` | Written |
| `eval_report.md` | Written |
