# DexHoldem Perception Eval Report

**Run ID:** p32_claude_split_batch010_claudebase_split_low  
**Problem ID:** p32  
**Date:** 2026-05-02  
**Source Image:** s_current/00_capture.jpg  

---

## Scene Assessment

| Check | Result | Confidence |
|---|---|---|
| Scene stable | Yes | 0.88 |
| Is my turn | Yes | 0.97 |
| Loop stage | to_recover | — |

The current frame is visually identical to s30. The robot arm is extended and low over the table near the chip area with no motion blur, indicating a settled (non-moving) pose.

---

## Blind / Role Assignment

| Role | Side |
|---|---|
| Dealer | Opponent |
| Small blind | Opponent |
| Big blind | Robot |

Confirmed by yellow "BIG BLIND" button on robot's side. Consistent with hole_card_cache.json (source: s0).

---

## Hole Cards (from cache)

- Left: **9d** (confidence 1.0, recognized at s5)
- Right: **5d** (confidence 1.0, recognized at s15)

---

## Community Cards

Two face-up cards are visible in the board area but **both are unreadable** due to occlusion by the robot arm and camera body. Card identities cannot be determined from this frame. Cards listed as empty pending a readable frame.

---

## Chip Inventory

| Denom | Robot | Opponent |
|---|---|---|
| 5 | 4 | 1 |
| 10 | 3 | 1 |
| 50 | 2 | 1 |
| 100 | 2 | 1 |

*Note: Robot arm occludes portions of both inventory areas; counts are estimates.*

---

## Current Bets

| Area | 5 | 10 | 50 | 100 |
|---|---|---|---|---|
| Robot (my) bet | 1 | 1 | 0 | 0 |
| Opponent bet | 2 | 1 | 1 | 0 |

*Note: Robot bet area partially occluded by arm; uncertain count.*

---

## Robot Behavior

- **Hand pose:** Extended and low over table, fingers open near surface (not in rest/idle pose)
- **Action in progress:** No
- **Recovery needed:** Yes
- **Safety OK:** Yes

The previous chip-push atom failed because the chip did not follow the finger. The chip layout remains intact and countable with no collateral disturbance. This is a retryable recovery state.

---

## Action Reasoning

**Loop stage is `to_recover` — no Texas Hold'em action decision was required.**  
The reasoning subagent was not invoked. Recovery assessment was performed by the robot-behavior-agent.

**Recommended next step:** Retry `recover_cached_action` — the interrupted chip-push. The table is intact and the condition is retryable. No human assistance required.

---

## Visual Subagents Run

All 7 subagents were launched in parallel (single wave, no serialization required):

1. scene-stability-agent
2. turn-detection-agent
3. community-cards-agent
4. chip-recognition-agent
5. bet-recognition-agent
6. robot-behavior-agent
7. blind-button-recognition-agent

Raw evidence files: `visual_raw/` (7 files)
