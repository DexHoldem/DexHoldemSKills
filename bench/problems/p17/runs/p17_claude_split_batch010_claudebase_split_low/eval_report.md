# Eval Report — p17_claude_split_batch010_claudebase_split_low

**State evaluated:** s17  
**Capture:** s17/00_capture.jpg  
**Date:** 2026-05-02

---

## Visual Subagent Results (9 agents, all run in parallel)

| Agent | Key Finding |
|---|---|
| scene-stability-agent | `scene_stable: true` — hand settled near table edge, card no longer mid-air |
| turn-detection-agent | `is_my_turn: true` — white "Your Turn" button visible in robot seat area |
| community-cards-agent | `community_cards: []` — all community card slots face-down (preflop) |
| chip-recognition-agent | `my_chips: 250, opponent_chips: 250` — both uncertain due to partial occlusion |
| bet-recognition-agent | `my_current_bet: 40, opponent_bet: 20` — opponent bet uncertain (robotic arm occlusion) |
| blind-button-recognition-agent | `dealer: opponent, small_blind: opponent, big_blind: robot` |
| robot-behavior-agent | `robot_idle: false, hand_empty: true, action_complete: true` — card placed, hand not yet at rest |
| held-card-recognition-agent | `card_held: false` — no card visible in hand grip |
| showdown-outcome-agent | `showdown_visible: false` — both hole card sets face-down, active hand |

---

## Action Sequence Context

- **sequence_id:** seq_view_right_hole_card  
- **loop_stage (sequence):** acting  
- **current_step:** put_down_card (status: dispatched)  
- **intent:** view_right_hole_card  
- **hole_card_cache:** left=9d (recognized), right=5d (recognized) — both cached

---

## Router Decision

**Route:** `wait`  
**Reason:** `loop_stage=acting` with `scene_stable=true` → robot action may still be moving or settling.  
**Agent required:** No  
**Suggested action:**
```json
{"action": "wait", "reason": "robot_acting", "sleep_seconds": 3}
```

The router does not call for Texas Hold'em poker action reasoning at this step (the loop_stage is `acting`, not `idle`). No reasoning-agent delegation was required.

---

## Parsed State Written

`s17/01_parsed_state.md` written with merged visual evidence. Key fields:

```json
{
  "loop_stage": "acting",
  "table": {
    "scene_stable": true,
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": 250,
    "opponent_chips": 250,
    "my_current_bet": 40,
    "opponent_bet": 20,
    "dealer": "opponent",
    "small_blind": "opponent",
    "big_blind": "robot",
    "robot_idle": false,
    "hand_empty": true,
    "action_complete": true,
    "card_held": false,
    "showdown_visible": false,
    "uncertain_fields": ["my_chips", "opponent_chips", "opponent_bet"]
  }
}
```

---

## Output Files

- `visual_raw/scene_stability.json`
- `visual_raw/turn_detection.json`
- `visual_raw/community_cards.json`
- `visual_raw/chip_recognition.json`
- `visual_raw/bet_recognition.json`
- `visual_raw/blind_button.json`
- `visual_raw/robot_behavior.json`
- `visual_raw/held_card.json`
- `visual_raw/showdown_outcome.json`
- `visual_summary.json`
- `eval_report.md`
- `s17/01_parsed_state.md` (written to problem dir)
