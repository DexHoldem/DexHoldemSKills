# DexHoldem Perception Eval Report

**Run ID:** p15_claude_split_batch010_claudebase_split_low  
**State:** s10  
**Image:** s10/00_capture.jpg  
**Date:** 2026-05-02

---

## Router Decision

| Field | Value |
|---|---|
| Route | **wait** |
| Reason | loop_stage=acting + scene_stable=false |
| Agent Required | No |
| Suggested Action | `{"action": "wait", "reason": "robot_acting", "sleep_seconds": 3}` |

The router determined that the robot is mid-action (pick_card dispatched for view_right_hole_card) and the scene is not stable. A wait is required before re-parsing.

---

## Visual Subagent Results (8 agents, run in parallel)

### 1. Scene Stability
- **scene_stable:** false
- **confidence:** 0.88
- The robot hand shifted position between s9 and s10; action still in progress.

### 2. Turn Detection
- **is_my_turn:** true
- **confidence:** 0.97
- "Your Turn" button clearly visible at robot seat.

### 3. Community Cards
- **community_cards:** [] (preflop)
- **confidence:** 0.92
- All 5 community slots show face-down card backs.

### 4. Chip Recognition
- **my_chips:** ~300, **opponent_chips:** ~385
- **confidence:** 0.35 (low — angled view, occlusion)

### 5. Bet Recognition
- **my_current_bet:** ~35, **opponent_bet:** ~35
- **confidence:** 0.45 (moderate uncertainty)

### 6. Robot Behavior
- **hand_pose:** unknown, **action_progress:** not_started
- **safety_concern:** false
- Robot hand near right hole-card area; no card visibly elevated.

### 7. Held Card Recognition
- **card_held:** false, **card:** null
- **confidence:** 0.15 (no card face readable)

### 8. Blind Buttons
- **dealer:** opponent, **small_blind:** opponent, **big_blind:** robot
- **confidence:** 0.85 (consistent with hole_card_cache blinds record)

---

## Action Sequence Context

| Field | Value |
|---|---|
| loop_stage | acting |
| intent | view_right_hole_card |
| current_step | pick_card (dispatched) |
| retry_count | 0 |
| consecutive_waits | 1 |
| total_waits | 1 |

---

## Hole Card Cache

| Slot | Card | Status |
|---|---|---|
| left | 9d | recognized (from s5) |
| right | null | unknown |

---

## Reasoning Agent

Not invoked. Route is `wait` — no poker action selection required while the robot is still executing an embodied action and the scene is unstable.

---

## Output Files

| File | Status |
|---|---|
| `visual_raw/scene_stability.json` | written |
| `visual_raw/turn_detection.json` | written |
| `visual_raw/community_cards.json` | written |
| `visual_raw/chip_recognition.json` | written |
| `visual_raw/bet_recognition.json` | written |
| `visual_raw/robot_behavior.json` | written |
| `visual_raw/held_card_recognition.json` | written |
| `visual_raw/blind_button_recognition.json` | written |
| `visual_summary.json` | written |
| `eval_report.md` | written |
| `s10/01_parsed_state.md` | written |
