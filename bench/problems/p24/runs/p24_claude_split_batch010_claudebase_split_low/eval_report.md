# DexHoldem Perception Eval Report

**Run ID:** p24_claude_split_batch010_claudebase_split_low  
**State:** s21  
**Image:** s21/00_capture.jpg  
**Date:** 2026-05-02

---

## Setup

- Visual setting: split (9 specialized visual subagents + 1 reasoning agent)
- All visual subagents run in parallel (single wave)
- No robot actions executed

---

## Visual Agent Results

| Agent | Key Finding |
|---|---|
| scene-stability-agent | `scene_stable: false` — robot arm extended over table in non-idle pose, mid-interrupted chip-push |
| turn-detection-agent | `is_my_turn: true` — "Your Turn" button visible near robot seat |
| community-cards-agent | `community_cards: []` — center obscured by robot arm; pre-flop |
| chip-recognition-agent | `my_chips: {5:4,10:3,50:4,100:4}` / `opponent_chips: {5:4,10:4,50:4,100:4}` — uncertain due to occlusion |
| bet-recognition-agent | `my_current_bet: 0` / `opponent_bet: 0` — no chips in betting lanes; chip 10 dropped, never placed |
| robot-behavior-agent | `robot_idle: false`, `hand_safe: true` — fingers open, no chip held, chip layout intact |
| blind-button-recognition-agent | `dealer: opponent`, `small_blind: opponent`, `big_blind: robot` (carried from s0 cache) |
| showdown-outcome-agent | `showdown_active: false` — pre-flop, no face-up cards, no showdown |

---

## Parsed State Summary (s21/01_parsed_state.md)

- **loop_stage:** to_recover (from action_sequence.json)
- **scene_stable:** false
- **is_my_turn:** true
- **community_cards:** []
- **my_chips:** {5:4, 10:3, 50:4, 100:4}
- **opponent_chips:** {5:4, 10:4, 50:4, 100:4}
- **my_current_bet:** {5:0, 10:0, 50:0, 100:0}
- **opponent_bet:** {5:0, 10:0, 50:0, 100:0}
- **uncertain_fields:** ["my_chips", "opponent_chips"]

---

## Router Decision

**Route:** `wait`  
**Reason:** loop_stage=`to_recover` with `scene_stable=false` triggers `route_wait(to_recover_scene_unstable)`. Per router.py, when loop_stage is "to_recover" and scene_stable is False, the system must wait for the scene to stabilize before attempting recovery retry.

**Suggested action:**
```json
{"action": "wait", "reason": "to_recover_scene_unstable", "sleep_seconds": 3}
```

---

## Reasoning Agent

Not invoked. The router routed to `wait` (no `choose_poker_action` required). The reasoning agent is only called when route=`choose_poker_action`.

---

## Context

The action_sequence.json (loop_stage="to_recover") notes: *"chip 10 drops along the way, no chip pushed by the finger, should recover cached action"*. This is a retryable physical failure — the robot's chip push was interrupted and the chip was dropped before reaching the betting area. Once the scene stabilizes (robot arm returns to idle/safe pose), the router will route to `recover_retryable` to retry the cached action.

---

## Output Files

- `visual_raw/scene-stability-agent.md` ✓
- `visual_raw/turn-detection-agent.md` ✓
- `visual_raw/community-cards-agent.md` ✓
- `visual_raw/chip-recognition-agent.md` ✓
- `visual_raw/bet-recognition-agent.md` ✓
- `visual_raw/robot-behavior-agent.md` ✓
- `visual_raw/blind-button-recognition-agent.md` ✓
- `visual_raw/showdown-outcome-agent.md` ✓
- `visual_summary.json` ✓
- `eval_report.md` ✓
- `s21/01_parsed_state.md` ✓
