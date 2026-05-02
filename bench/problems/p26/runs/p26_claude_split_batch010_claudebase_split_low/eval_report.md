# DexHoldem Perception Eval Report

**Run ID:** p26_claude_split_batch010_claudebase_split_low  
**State:** s23  
**Image:** s23/00_capture.jpg  
**Date:** 2026-05-02

---

## Visual Agent Results (9 agents, run in parallel)

| Agent | Key Finding | Confidence |
|---|---|---|
| scene-stability-agent | Scene stable; frames s22↔s23 nearly identical | 0.92 |
| turn-detection-agent | `is_my_turn: true` — "Your Turn" button visible bottom-left | 0.97 |
| community-cards-agent | `community_cards: []` — preflop, no board cards | 0.92 |
| chip-recognition-agent | my={5:5,10:3,50:2,100:3} opp={5:3,10:2,50:1,100:2} | moderate/low |
| bet-recognition-agent | my_bet={5:2,10:2}=20 opp_bet={5:2,10:1}=15 | low |
| blind-button-recognition-agent | dealer=opponent, SB=opponent, BB=robot | high |
| held-card-recognition-agent | Not visible in frame; cache: left=9d, right=5d | 0.92 |
| robot-behavior-agent | Hand extended over central pot zone, action not complete, safety OK, no recovery needed | 0.68 |
| showdown-outcome-agent | No showdown; active betting round | 0.88 |

---

## Merged State

- **Scene stable:** yes  
- **My turn:** yes  
- **Community cards:** none (preflop)  
- **Hole cards (cache):** 9♦ + 5♦  
- **My chips (inventory):** 5×5, 3×10, 2×50, 3×100 = 580  
- **Opponent chips (inventory):** 3×5, 2×10, 1×50, 2×100 = 295  
- **My current bet:** 2×5 + 2×10 = 30  
- **Opponent current bet:** 2×5 + 1×10 = 20  
- **Blind assignment:** robot = big blind, opponent = dealer/small blind

---

## Loop Stage Assessment

Prior state (s22) loop_stage was **to_recover** — chip stuck mid-push.

Visual evidence from s23:
- Robot hand is extended over the central pot zone (not at rest/idle pose).
- The s22 stuck-chip condition is **not visually persisting** — the hand has advanced to the pot area, suggesting the push reached its destination.
- However, the hand has **not yet returned to rest**, so `action_complete = false`.
- `recovery_needed = false` (no unsafe condition detected).

**Assessment:** Loop stage remains `to_recover` pending hand return to rest. Once the hand settles at idle, the executor should re-evaluate whether the action succeeded (bet chips now visible in betting area) or requires a further retry.

---

## Reasoning Agent

Not called. The current loop stage is `to_recover` (not `idle`/`choose_poker_action`), so Texas Hold'em action reasoning was not required at this step.

---

## Raw Evidence Files

All 9 agent evidence files written to `visual_raw/`:
- `scene-stability-agent.md`
- `turn-detection-agent.md`
- `community-cards-agent.md`
- `chip-recognition-agent.md`
- `bet-recognition-agent.md`
- `blind-button-recognition-agent.md`
- `held-card-recognition-agent.md`
- `robot-behavior-agent.md`
- `showdown-outcome-agent.md`
