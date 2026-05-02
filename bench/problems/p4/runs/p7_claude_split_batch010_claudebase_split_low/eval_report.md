# DexHoldem Perception Eval Report

**Run ID:** p7_claude_split_batch010_claudebase_split_low  
**State:** s5  
**Image:** s5/00_capture.jpg  
**Loop Stage:** atom_idle  
**Active Action:** view_card (left hole card)

---

## Visual Agent Results (9 agents, run in parallel)

| Agent | Key Finding | Confidence |
|-------|-------------|------------|
| scene-stability | scene_stable=**false** — card upright, robot in motion | 0.75 |
| turn-detection | is_my_turn=**true** — "Your Turn" button at robot seat | 0.88 |
| community-cards | community_cards=**[]** (uncertain observation of 6d rejected) | 0.35 |
| chip-recognition | my_chips={5:4,10:6,50:2,100:3}; opp={5:3,10:5,50:2,100:2} | 0.35 |
| bet-recognition | my_bet={5:2,10:3}; opp_bet={5:2,10:2} | 0.35 |
| robot-behavior | action_complete=true, card_visible=true, card=**5d**, safety_ok | 0.88 |
| held-card | card=**5d**, slot=left — **conflicts with cache (9d)** | 0.82 |
| blind-buttons | dealer=opponent, small_blind=opponent, big_blind=robot | 0.90 |
| showdown-outcome | showdown_detected=false | 0.82 |

---

## Synthesis

The robot is executing a `view_card` action for the left hole card (loop_stage=`atom_idle`). Both the robot-behavior agent and the held-card agent independently read the card as **5 of Diamonds (5d)**.

This conflicts with the current hole-card cache entry of `9d` (set at s5 with confidence 1.0). Both agents examining the live card in s5 read it as 5d with confidence 0.82–0.88. The cache should be updated to 5d.

Scene is **not stable** per the scene-stability agent (confidence 0.75), consistent with the robot arm being in an active hold pose. However, the robot-behavior agent assesses the view_card action as complete.

No poker action reasoning was needed: the current step is card reading within the view_card sequence, not a betting decision.

---

## Recommended Next Steps

1. **Update hole-card cache**: left card → `5d` (overwrite cached `9d`).
2. **Continue view_card sequence**: proceed to `put_down_card` step.
3. **Do not execute a poker betting action** until the robot returns to idle and scene stability is confirmed.

---

## Raw Evidence Files

- `visual_raw/scene_stability.json`
- `visual_raw/turn_detection.json`
- `visual_raw/community_cards.json`
- `visual_raw/chip_recognition.json`
- `visual_raw/bet_recognition.json`
- `visual_raw/robot_behavior.json`
- `visual_raw/held_card.json`
- `visual_raw/blind_buttons.json`
- `visual_raw/showdown_outcome.json`
