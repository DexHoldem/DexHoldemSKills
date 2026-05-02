# Perception Eval Report

**Run ID**: p34_claude_split_terminal_quicktest_claude_sonnet_low
**Problem**: p34
**State**: s_current
**Capture**: s_current/00_capture.jpg (1920×1080, JPEG)
**Date**: 2026-05-02

---

## Visual Subagents (Wave 1 — Parallel)

All six visual subagents ran in parallel against `s_current/00_capture.jpg`.

| Agent | Result | Confidence |
|---|---|---|
| scene-stability-agent | Stable | High |
| turn-detection-agent | is_my_turn = true | High |
| community-cards-agent | 5 cards visible (river); reads uncertain | Low |
| chip-recognition-agent | Robot ~175, Opponent ~270 | Low (occluded) |
| bet-recognition-agent | My bet ~20, Opponent ~15 | Low (occluded) |
| robot-behavior-agent | Hand at idle/rest, no action in progress | High |

---

## Merged Visual State

```json
{
  "scene_stable": true,
  "is_my_turn": true,
  "board_stage": "river",
  "community_cards_best_effort": ["8d?", "Kd?", "6s?", "6d?", "6c?"],
  "my_chips_visual": 175,
  "opponent_chips_visual": 270,
  "my_current_bet_visual": 20,
  "opponent_bet_visual": 15,
  "robot_hand_pose": "idle",
  "uncertain_fields": [
    "community_cards",
    "my_chips",
    "opponent_chips",
    "my_current_bet",
    "opponent_bet"
  ]
}
```

### Context from Previous States

- s30 parsed state showed board = [Qh, 7d, 6s, Jc] (turn), robot pushing 100-chip raise
- Robot hole cards cached: left=9d, right=5d
- After s30 action: my_current_bet ≈ 260–270, opponent_bet ≈ 160

The bet-area visual counts (~20 and ~15) are likely severe undercounts due to the robot arm occluding the right side of the bet area. The chip inventory counts are similarly affected.

---

## Router Decision

**Route**: `resolve_uncertain_fields`

The router would block `choose_poker_action` because `uncertain_fields` is non-empty. Multiple fields require resolution before a safe poker action can be committed:

1. `community_cards` — visual reads conflict with s30 state for positions 1, 2, 4; camera angle and chip occlusion make individual card reads unreliable.
2. `my_chips` — robot arm occludes right-side inventory; visual count (175) is far below context-estimated value (~400).
3. `opponent_chips` — partially occluded and angled; visual count (270) uncertain.
4. `my_current_bet` — visual count (20) is implausibly low given robot raised in s30; severe occlusion likely.
5. `opponent_bet` — visual count (15) similarly implausible; severe occlusion likely.

---

## Reasoning Agent (Conditional — Run Despite Uncertain Fields)

The reasoning agent was run for eval purposes to capture a strategic recommendation.

**Hole cards**: 9d, 5d
**Board**: River — candidate boards:
- Candidate A (visual): 8d, Kd, 6s, 6d, 6c → robot makes King-high diamond flush (strong)
- Candidate B (context): Qh, 7d, 6s, Jc + unknown river card → robot is weak (nine-high)

**Recommendation**: `check`

**Reasoning**: Board uncertainty makes it risky to commit more chips. Checking forces opponent to reveal strength. If board A is confirmed (flush made), a value raise or call of opponent's bet becomes strongly preferred. If board B, checking avoids a costly bluff.

**Caveats**:
- Must verify `check` is available (no unmatched opponent river bet).
- If Kd and two other diamonds confirmed on board, robot has a near-nut flush and should bet for value.
- All bet/chip amounts must be confirmed before any raise.

---

## Output Files

- `visual_raw/scene_stability.md` — scene-stability-agent evidence
- `visual_raw/turn_detection.md` — turn-detection-agent evidence
- `visual_raw/community_cards.md` — community-cards-agent evidence
- `visual_raw/chip_recognition.md` — chip-recognition-agent evidence
- `visual_raw/bet_recognition.md` — bet-recognition-agent evidence
- `visual_raw/robot_behavior.md` — robot-behavior-agent evidence
- `visual_summary.json` — merged visual state and router decision
- `eval_report.md` — this file

---

## Summary

Scene is stable and it is the robot's turn (both high-confidence). Five community cards are visible (river), but individual card reads and chip/bet counts are all uncertain due to camera angle and robot arm occlusion. The router would route to `resolve_uncertain_fields`. Conditional reasoning-agent recommendation is `check`, pending board and bet count verification. No robot actions were executed.
