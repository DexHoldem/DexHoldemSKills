# DexHoldem Perception Eval Report

**Run ID:** p22_claude_split_batch010_claudebase_split_low  
**Problem ID:** p22  
**State evaluated:** s20  
**Image:** s20/00_capture.jpg  

---

## Visual Agent Results Summary

| Agent | Key Finding |
|---|---|
| scene-stability-agent | **UNSTABLE** — robot arm still extended over table, large positional change from s19 |
| turn-detection-agent | **Robot's turn** — "Your Turn" button clearly visible on robot seat side |
| robot-behavior-agent | Chip-push action at or near completion; hand settled low over chip area, no blur; possibly still in final withdraw phase |
| community-cards-agent | **0 community cards** — community row fully occluded by robot arm; carry forward pre-flop (empty) |
| chip-recognition-agent | Robot inventory: ~{5:4, 10:4}; green/brown occluded — carry forward {50:4, 100:4}. Opponent: ~{5:4, 10:4}; green/brown not readable |
| bet-recognition-agent | Bet counts uncertain; robot arm mid-action over betting lane; scene not stable for reliable count |
| blind-button-recognition-agent | Buttons not visible; carry forward: dealer=opponent, small_blind=opponent, big_blind=robot |
| held-card-recognition-agent | No card held up/readable; cache retained: left=9d, right=5d |
| showdown-outcome-agent | No showdown in progress; no face-up cards; no win/lose determinable |

---

## Merged State

```json
{
  "blind": "big_blind",
  "loop_stage": "acting",
  "intent": "wait_for_motion_completion",
  "robot": "acting pushing chips 10, wait",
  "table": {
    "scene_stable": false,
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {"5": 4, "10": 4, "50": 4, "100": 4},
    "opponent_chips": {"5": 4, "10": 4, "50": 4, "100": 4},
    "my_current_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "opponent_bet": {"5": 0, "10": 0, "50": 0, "100": 0}
  }
}
```

---

## Reasoning Agent

Not invoked. The current intent is `wait_for_motion_completion` — the robot is mid-action pushing chips. No `choose_poker_action` request is warranted until the scene is stable and the motion has completed. Poker action reasoning is deferred to the next stable capture.

---

## Decision

**Action: WAIT**

The scene is unstable. The robot arm remains extended over the table in an active pose consistent with a chip-push action that has not yet fully resolved. The correct response is to wait for the next capture and re-evaluate once the arm has returned to its rest position and the scene has stabilized.

No robot actions are executed.

---

## Occlusion Warnings

- Robot arm heavily occludes robot inventory zone (green/brown chips unreadable from s20)
- Robot arm occludes the community card row (no community cards readable)
- Robot arm partially occludes the betting lane (bet counts uncertain)

---

## Evidence Files

All raw evidence files written to:  
`runs/p22_claude_split_batch010_claudebase_split_low/visual_raw/`

- scene-stability-agent.md
- turn-detection-agent.md
- robot-behavior-agent.md
- community-cards-agent.md
- chip-recognition-agent.md
- bet-recognition-agent.md
- blind-button-recognition-agent.md
- held-card-recognition-agent.md
- showdown-outcome-agent.md
