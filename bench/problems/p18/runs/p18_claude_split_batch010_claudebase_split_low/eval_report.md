# DexHoldem Perception Eval Report

**Run ID:** p18_claude_split_batch010_claudebase_split_low  
**State:** s18  
**Date:** 2026-05-02  

---

## 1. Perception Pipeline Summary

### Visual Agents (Wave 1 — all parallel)

| Agent | Result |
|---|---|
| scene-stability-agent | **Stable** — hand settled, no motion between s17→s18 |
| turn-detection-agent | **is_my_turn = true** — "Your Turn" button clearly visible at robot seat |
| community-cards-agent | **0 community cards** — preflop, all slots face-down |
| chip-recognition-agent | Robot ~160 chips, Opponent ~355 chips (partial occlusion) |
| bet-recognition-agent | Robot bet = 50 (confident), Opponent bet = ~30 (uncertain ±10) |
| blind-button-recognition-agent | Dealer/SB = opponent, BB = robot |
| robot-behavior-agent | **Idle/safe** — near rest pose, not holding card or chips |
| showdown-outcome-agent | **No showdown** — all cards face-down, active hand preflop |
| held-card-recognition-agent | **No held card** — robot hand at rest, not gripping |

### Hole Cards (from cache)

Both hole cards were previously viewed and cached:
- **Left slot:** 9♦ (9d)
- **Right slot:** 5♦ (5d)
- **Hand:** 9♦-5♦ — suited (both diamonds)

---

## 2. Router Decision

**Route:** `choose_poker_action`

**Routing path:**
1. `capture_exists`: ✓ s18/00_capture.jpg present
2. `parsed_state_exists`: visual_parse triggered → wrote s18/01_parsed_state.md
3. `parsed_state_valid`: ✓ table object with required fields
4. `loop_stage`: idle (confirmed from action_sequence.json — all view-card steps complete)
5. `scene_stable`: ✓ true
6. `is_my_turn`: ✓ true
7. `hole_cards_cached`: ✓ left=9d, right=5d
8. `uncertain_fields`: none blocking
9. → **choose_poker_action**

---

## 3. Poker Reasoning (reasoning-agent)

**Hand:** 9♦ 5♦ suited  
**Street:** Preflop  
**Position:** Big Blind (out of position post-flop)  
**Opponent:** Small Blind / Dealer  

**Analysis:**
- 9d-5d is a marginal speculative hand: weak raw equity, but diamond flush draw potential.
- Robot is BB (50 chips posted). Opponent appears to have posted only the small blind (~30 chips), with no raise above the BB detected.
- As BB, if opponent has not raised, the robot can **check** to see the flop for free.
- Raising would build a large pot with a weak hand while out of position post-flop (BB acts first post-flop in heads-up).
- Folding forfeits the already-posted big blind with a hand that has live improvement potential.

**Recommendation:** `check`

**Validation:** Check is confirmed as optimal. The reasoning agent's analysis is consistent with standard heads-up big blind strategy — take the free card with a marginal suited hand and re-evaluate post-flop.

---

## 4. Final Action

```json
{"action": "check", "reason": "Robot holds 9d-5d suited as Big Blind preflop. Opponent bet appears to be the posted small blind only (no raise above BB). Checking takes the free flop with a speculative hand rather than inflating the pot out of position."}
```

**(No robot action executed — eval mode only.)**

---

## 5. Output Files

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
| `visual_raw/held_card_recognition.json` | ✓ written |
| `visual_summary.json` | ✓ written |
| `eval_report.md` | ✓ written |
| `s18/01_parsed_state.md` | ✓ written |
| `s18/02_action.md` | ✓ written |

---

## 6. Notable Observations

- **Opponent bet uncertainty:** The opponent's current bet was estimated at 30 chips but flagged as uncertain (±10). This minor uncertainty does not affect the poker action decision since the action is a check (no call amount required).
- **Chip inventory occlusion:** Both inventory counts are understated due to the robot arm obscuring the right side of the table. Total stacks are approximations; the robot is likely shorter-stacked than the opponent.
- **Showdown agent note:** The showdown agent initially suggested `show_hand` loop stage, but this was overridden by the action_sequence.json confirmation (all view-card steps complete) and the absence of any face-up opponent cards. Correct stage is `idle`.
