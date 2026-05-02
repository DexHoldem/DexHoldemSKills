# DexHoldem Perception Eval Report

**Run ID:** p30_claude_split_batch010_claudebase_split_low  
**Scenario:** s28  
**Date:** 2026-05-02  
**Image:** s28/00_capture.jpg

---

## Visual Perception Summary

| Agent | Finding | Confidence |
|---|---|---|
| scene-stability | Stable — robot arm retracted, table fully visible | 0.88 |
| turn-detection | Robot's turn (Your Turn button visible) | 0.97 |
| community-cards | 7d 6s 6d 6c 6s — River (5 cards) | High pos 1-2 / Low pos 3-5 |
| held-cards | 9d 5d (from cache, s5/s15) | 1.0 |
| chip-recognition | Robot ~30 chips; Opponent larger stack | Low-moderate |
| bet-recognition | Robot bet in ~30; Opponent bet in ~70 | Low-moderate |
| blind-buttons | Robot = Big Blind; Opponent = Small Blind / Dealer | High |
| robot-behavior | Idle pose, safe, no active motion | High |
| showdown-outcome | No showdown — hole cards face-down | High |

---

## Game State

- **Street:** River
- **Board:** 7d 6s 6d 6c 6s (four 6s — heavily paired board; some card-read uncertainty at positions 3–5)
- **Robot hand:** 9d 5d → effective hand: quad 6s with 9 kicker
- **Position:** Robot is Big Blind (out of position post-flop)
- **Action facing:** Opponent bet ~70 total vs robot's ~30 in; robot faces ~40 call

---

## Reasoning Agent Recommendation

**Action: FOLD**  
**Confidence: 0.82**

On a quad-6 board the winner is determined entirely by kicker. The robot's 9-kicker loses to any opponent card above a 9 (T, J, Q, K, A), which covers the majority of likely holdings. The opponent's river aggression (bet significantly more than robot's current contribution) strongly signals a superior kicker for value. Pot odds of approximately 2.5:1 require ~29% equity to break even, but the robot's probability of holding the best kicker is well below that threshold. Fold avoids committing additional chips in a likely losing spot.

**Primary caveat:** Community card read uncertainty at positions 3–5. If the board is misread and contains fewer than four 6s, the robot may hold a stronger hand (e.g., a full house), which would change the recommendation. The visual subagents flagged low confidence on those positions.

---

## Output Files

| File | Status |
|---|---|
| visual_raw/scene_stability.json | Written |
| visual_raw/turn_detection.json | Written |
| visual_raw/community_cards.json | Written |
| visual_raw/held_cards.json | Written |
| visual_raw/chip_recognition.json | Written |
| visual_raw/bet_recognition.json | Written |
| visual_raw/blind_buttons.json | Written |
| visual_raw/robot_behavior.json | Written |
| visual_raw/showdown_outcome.json | Written |
| visual_summary.json | Written |
| eval_report.md | Written |

---

## Action Decision

**Recommended action: fold**  
No robot execution performed (execution explicitly excluded per task instructions).
