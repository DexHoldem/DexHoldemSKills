# DexHoldem Perception Eval Report

**Run ID**: p23_claude_split_batch010_claudebase_split_low  
**Problem ID**: p23  
**State**: s22  
**Date**: 2026-05-02

---

## 1. Pipeline Overview

Six visual subagents were run in parallel on `s22/00_capture.jpg`. No robot actions were executed. The reasoning subagent was not invoked (route does not require poker action selection).

---

## 2. Visual Agent Results

| Agent | Key Finding | Confidence |
|---|---|---|
| scene-stability-agent | `scene_stable: true` — s21 and s22 frames near-identical, hand settled | 0.93 |
| turn-detection-agent | `is_my_turn: true` — "Your Turn" button clearly visible at robot seat | 0.97 |
| community-cards-agent | `community_cards: []` — no face-up cards in board zone (preflop) | 0.75 |
| chip-recognition-agent | Counts uncertain; robot arm occludes inventory area | 0.35 |
| bet-recognition-agent | Counts uncertain; betting area partially occluded | 0.35 |
| robot-behavior-agent | `hand_pose: placing_chip`, `action_in_progress: true`, `safety_ok: true` | 0.72 |

### Chip / Bet Merge Decision

Chip and bet raw counts from this frame are low-confidence (0.35) due to robot arm occlusion. The values from s21 (all zeros for bets; 4×4 grid for chips: `{5:4, 10:4, 50:4, 100:4}`) are used as the fallback and the fields are marked as `uncertain_fields`.

---

## 3. Parsed State Written

`s22/01_parsed_state.md` was written with:

```json
{
  "loop_stage": "to_recover",
  "table": {
    "scene_stable": true,
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {"5": 4, "10": 4, "50": 4, "100": 4},
    "opponent_chips": {"5": 4, "10": 4, "50": 4, "100": 4},
    "my_current_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "opponent_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "uncertain_fields": ["my_chips", "opponent_chips", "my_current_bet", "opponent_bet"]
  }
}
```

---

## 4. Router Decision

The router was traced manually through `router.py`:

- `loop_stage = to_recover` (from action_sequence.json fallback)
- `scene_stable = true` → do not wait
- `current_step = "recover_cached_action"`, `status = "pending"`
- `has_cached_command_step` → **False** (no `command` key in the step object)
- `retry_count = 1`, `max_step_retries = 2` → within limit
- `total_recoveries = 0`, `max_total_recoveries = 8` → within limit

**Route**: `recover_retryable`  
**Agent required**: Yes — `recover_retryable_action`  
**Context passed**:
```json
{
  "current_step": "recover_cached_action",
  "last_error": "Previous intended motion was interrupted or did not reach the expected destination.",
  "intent": "recover_cached_action",
  "action": null,
  "plan": null,
  "steps": [{"name": "recover_cached_action", "status": "pending", "description": "Previous intended motion was interrupted or did not reach the expected destination."}]
}
```

---

## 5. Reasoning Agent

Not invoked. The route is `recover_retryable_action`, which requires physical recovery judgment — not Texas Hold'em poker strategy. The reasoning subagent is reserved for `choose_poker_action` routes.

---

## 6. Hole Card Cache

Both hole cards are cached from earlier states:

| Slot | Card | Source |
|---|---|---|
| Left | 9♦ (9d) | s5 |
| Right | 5♦ (5d) | s15 |

---

## 7. Output Files

| File | Status |
|---|---|
| `runs/p23_claude_split_batch010_claudebase_split_low/visual_raw/scene_stability.json` | Written |
| `runs/p23_claude_split_batch010_claudebase_split_low/visual_raw/turn_detection.json` | Written |
| `runs/p23_claude_split_batch010_claudebase_split_low/visual_raw/community_cards.json` | Written |
| `runs/p23_claude_split_batch010_claudebase_split_low/visual_raw/chip_recognition.json` | Written |
| `runs/p23_claude_split_batch010_claudebase_split_low/visual_raw/bet_recognition.json` | Written |
| `runs/p23_claude_split_batch010_claudebase_split_low/visual_raw/robot_behavior.json` | Written |
| `runs/p23_claude_split_batch010_claudebase_split_low/visual_summary.json` | Written |
| `runs/p23_claude_split_batch010_claudebase_split_low/eval_report.md` | Written |
| `s22/01_parsed_state.md` | Written |

No robot action was executed (`02_action.md` not written per task instructions).
