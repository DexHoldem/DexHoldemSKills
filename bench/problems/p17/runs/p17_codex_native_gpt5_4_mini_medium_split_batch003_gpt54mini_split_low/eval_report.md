# DexHoldem Perception Report

State `s17` was assessed from `s17/00_capture.jpg` using only subagent evidence.

## Summary

- `is_my_turn`: yes
- `scene_stable`: no
- Community cards: 5 visible, all face-down/unreadable
- Dealer / blinds: dealer opponent, small blind opponent, big blind robot
- Robot hand: still extended and holding a card
- Showdown: not visible, unresolved

## Evidence Merge

- The turn-button subagent found the white turn button at the lower-left of the table near seat 6.
- The community-card subagent reported five face-down cards, unreadable left to right.
- The blind-button subagent identified the opponent as dealer and small blind, with the robot as big blind.
- The bet-recognition subagent saw opponent-side chips as 3 red, 3 blue, and an occluded mixed cluster on the right; robot-side chips as 4 red, 4 blue, and 2 green.
- The chip-recognition subagent reported robot inventory as 4 red and 4 blue, and opponent inventory as 3 red, 5 blue, plus a partly occluded 2 green and 3 brown cluster.
- The held-card subagent saw a robot-held card with a visible red `5` corner, but not enough to read the full card.
- The robot-behavior subagent said the hand is still in progress, safe, and not near rest pose.
- The scene-stability subagent marked the frame unstable because the robot hand is still gripping a card.
- The showdown subagent reported no visible showdown and no clear win/lose evidence.

## Decision

No robot action was executed. The correct output for this perception step is a merged state snapshot with unresolved visual action still in progress.
