# DexHoldem Perception Eval Report

**Run ID:** p25_claude_split_batch010_claudebase_split_low  
**Problem ID:** p25  
**State:** s23  
**Date:** 2026-05-02  

---

## Visual Perception Summary

### Scene Status
| Check | Result | Confidence |
|---|---|---|
| Scene stable | ✅ Yes | 0.92 |
| Is my turn | ✅ Yes | 0.97 |
| Showdown in progress | ❌ No | 0.85 |
| Robot holding card | ❌ No | 0.85 |
| Robot safety OK | ✅ Yes | 0.62 |

### Cards
- **Hole cards:** 9♦ (left, cached from s5), 5♦ (right, cached from s15)
- **Community cards:** None — preflop
- **Street:** Preflop

### Blinds / Position
- **Dealer:** Opponent
- **Small Blind:** Opponent
- **Big Blind:** Robot (confirmed by yellow BB button in s23 + cache from s0)
- Confidence: 0.88

### Chip Inventory (using s22 parsed state as high-confidence fallback)
| Player | 5 | 10 | 50 | 100 | Total |
|---|---|---|---|---|---|
| Robot | 4 | 3 | 4 | 4 | 650 |
| Opponent | 4 | 4 | 4 | 4 | 660 |

*Note: s23 chip-recognition-agent had confidence 0.35 due to oblique angle and robot arm occlusion. s22 parsed state used instead.*

### Current Bets
| Player | 5 | 10 | 50 | 100 | Total |
|---|---|---|---|---|---|
| Robot (BB posted) | 0 | 1 | 0 | 0 | 10 |
| Opponent | 0 | 0 | 0 | 0 | 0 |

*Baseline from s22 parsed state. Bet agent s23 reading (confidence 0.45) showed uncertainty; s22 baseline used as primary.*

---

## Subagent Evidence Files

All evidence written to `visual_raw/`:
- `scene_stability.json` — stable: true (0.92)
- `turn_detection.json` — is_my_turn: true (0.97)
- `community_cards.json` — []: preflop (0.92)
- `chip_recognition.json` — low confidence s23 reading (0.35)
- `bet_recognition.json` — uncertain read (0.45)
- `robot_behavior.json` — extended_over_table, safety_ok (0.62)
- `held_card.json` — not holding (0.85)
- `blind_button.json` — opponent dealer/SB, robot BB (0.88)
- `showdown_outcome.json` — no showdown (0.85)

---

## Reasoning Agent Recommendation

**Action: CHECK**  
**Confidence: 0.72**

**Justification:**  
The robot holds 9♦ 5♦ as big blind in a heads-up preflop situation. This is a marginal suited hand — not strong enough to build a large pot preflop voluntarily. The opponent most likely called the big blind (matching 10 chips), giving the robot the option to check and see a free flop. Checking preserves chips and lets the suited-connector nature of 9d 5d develop into a potential flush draw. No raise is warranted; no fold is warranted since the check costs nothing if opponent called.

**Caveats:**  
- If the bet agent's reading is accurate and opponent raised to 20, check would be invalid and a call for 10 more chips would be the appropriate substitution.
- Robot behavior agent observed the hand extended over the table (not at rest), which may indicate a prior action still settling. This does not block the recommended check.

---

## Action Decision

```json
{
  "action": "check",
  "amount": null,
  "source": "reasoning-agent",
  "validated": true
}
```
