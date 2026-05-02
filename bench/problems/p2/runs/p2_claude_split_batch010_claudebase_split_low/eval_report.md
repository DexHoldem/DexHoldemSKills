# DexHoldem Perception Eval Report

**Run ID:** p2_claude_split_batch010_claudebase_split_low  
**State:** s0  
**Image:** s0/00_capture.jpg  
**Harness:** claude / split-visual variant  

---

## Visual Subagent Results (9 agents, run in parallel)

| Agent | Key Finding |
|---|---|
| scene-stability-agent | `scene_stable: true` — robot idle, no motion blur, image clear |
| turn-detection-agent | `is_my_turn: null` — turn button not identifiable |
| community-cards-agent | `community_cards: []` — all board slots face-down (preflop) |
| chip-recognition-agent | `my_chips: 420`, `opponent_chips: 405` (uncertain, partial occlusion) |
| bet-recognition-agent | `my_current_bet: 30`, `opponent_bet: 10` (uncertain, angled view) |
| blind-button-recognition-agent | `dealer: opponent`, `small_blind: opponent`, `big_blind: robot` |
| held-card-recognition-agent | `held_card: null` — robot not holding any card |
| robot-behavior-agent | `robot_idle: true`, `safety_ok: true` — hand at rest, no action in progress |
| showdown-outcome-agent | `showdown_active: false`, `outcome: null` — no showdown |

---

## Merged Table State

```json
{
  "scene_stable": true,
  "is_my_turn": null,
  "community_cards": [],
  "my_chips": 420,
  "opponent_chips": 405,
  "my_current_bet": 30,
  "opponent_bet": 10,
  "dealer": "opponent",
  "small_blind": "opponent",
  "big_blind": "robot",
  "held_card": null,
  "robot_idle": true,
  "safety_ok": true,
  "showdown_active": false,
  "uncertain_fields": ["is_my_turn", "my_chips", "opponent_chips", "my_current_bet", "opponent_bet"]
}
```

---

## Router Judgment

**Route:** `resolve_turn`  
**Reason:** Scene is stable, loop_stage is `idle`, but `is_my_turn` could not be determined from this capture. The white turn button was not identifiable — only the yellow BIG BLIND and a blue opponent-side button were visible. Per router logic, turn must be resolved before any poker action or card-view sequence can proceed.

**Agent required:** yes (`resolve_turn` task)

---

## Blind / Position Summary

Under the two-player (heads-up) rule:
- **Robot:** Big Blind
- **Opponent (human):** Dealer + Small Blind

The yellow BIG BLIND button at the robot seat and the blue dealer/SB button at the opponent seat confirm this assignment.

---

## Uncertain Fields

The following fields carry elevated uncertainty due to camera angle and partial occlusion:

- `is_my_turn` — turn button not identified (primary blocker)
- `my_chips` / `opponent_chips` — brown chip stacks partially occluded; robot arm partially blocks robot-side stack
- `my_current_bet` / `opponent_bet` — center bet area viewed at an angle; counts approximate

---

## No Reasoning Agent Invoked

The reasoning agent (poker action selection) was not invoked because the router did not reach `choose_poker_action`. The scene requires turn resolution first.

---

## Output Files

- `visual_raw/scene_stability.json`
- `visual_raw/turn_detection.json`
- `visual_raw/community_cards.json`
- `visual_raw/chip_recognition.json`
- `visual_raw/bet_recognition.json`
- `visual_raw/blind_button_recognition.json`
- `visual_raw/held_card_recognition.json`
- `visual_raw/robot_behavior.json`
- `visual_raw/showdown_outcome.json`
- `visual_summary.json`
- `eval_report.md`
