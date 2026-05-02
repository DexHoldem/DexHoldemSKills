# DexHoldem Perception Eval Report

**Run ID:** p20_claude_split_batch010_claudebase_split_low  
**State:** s18  
**Image:** s18/00_capture.jpg  
**Date:** 2026-05-02

---

## Router Decision

The router found `s18/00_capture.jpg` present but `s18/01_parsed_state.md` absent, routing to **`visual_parse`**. Nine visual subagents were launched in parallel to produce the parsed state.

---

## Visual Subagent Results

| Agent | Finding |
|---|---|
| scene-stability | `scene_stable: false` — hand transitional between acting and idle pose |
| turn-detection | `is_my_turn: true` — "Your Turn" button visible at robot seat |
| community-cards | `[]` — all five slots face-down, no board cards readable |
| chip-recognition | Robot: {5:4, 10:3}; Opponent: {5:2, 10:4, 100:2} |
| bet-recognition | My bet: {5:3, 10:2}; Opponent bet: {5:2, 10:2} |
| robot-behavior | `robot_state: idle`, `held_card: null`, `is_safe: true` |
| held-card-recognition | `holding_card: false` — no card gripped in s18 |
| blind-button-recognition | dealer=opponent, small_blind=opponent, big_blind=robot |
| showdown-outcome | `showdown_in_progress: false`, no winner yet |

---

## Loop Stage Determination

**loop_stage: `down`**

Prior `action_sequence.json` has `loop_stage=down` with `human_required=true` and `current_step=put_down_card` marked `failed`. State s17 was `loop_stage=acting` with scene_stable=false (robot mid-motion for right hole-card put-down of 5d). In s18, the robot hand has returned to near-idle and no card is held, but the scene stability agent flags the pose as still transitional. Since the sequence was in an error/down state requiring human intervention, `loop_stage=down` is carried forward.

---

## Reasoning Agent

Not invoked. The `down` loop stage routes to `recover_down`, which requires human inspection — poker action selection is not applicable at this point.

---

## Hole Card Cache

- Left: **9d** (recognized at s5, confidence 1.0)
- Right: **5d** (recognized at s15, confidence 1.0)

Both hole cards are cached. The right card (5d) was the subject of the failed put_down_card sequence.

---

## Outputs Written

| File | Status |
|---|---|
| `s18/01_parsed_state.md` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_raw/scene_stability.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_raw/turn_detection.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_raw/community_cards.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_raw/chip_recognition.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_raw/bet_recognition.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_raw/robot_behavior.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_raw/held_card.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_raw/blind_buttons.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_raw/showdown_outcome.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/visual_summary.json` | Written |
| `runs/p20_claude_split_batch010_claudebase_split_low/eval_report.md` | Written |

---

## Next Step (Router)

With `s18/01_parsed_state.md` now written containing `loop_stage=down`, the router will next route to **`recover_down`** — requiring agent judgment to inspect the scene and decide between retry, wait, or request_human. Since `human_required=true` is already set in `action_sequence.json`, the expected outcome is a `request_human` action in `s18/02_action.md`.
