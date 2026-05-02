# Perception Step Report

Latest capture: `s17/00_capture.jpg`

## Outcome
- Scene stability: unstable
- Turn ownership: it is our turn
- Community cards: no face-up community cards visible
- Held card: readable `3d`
- Robot behavior: mid-action, not settled

## Evidence
- The scene stability subagent compared `s16/00_capture.jpg` and `s17/00_capture.jpg` and reported the robot hand is still holding a card and has not settled.
- The turn detection subagent found the white `Your Turn` button near the lower-left robot seat.
- The community cards subagent reported only card backs in the center row.
- The bet recognizer found `6` red 5-chips and `5` blue 10-chips on the left bet area; the right bet area is partially occluded, with `2` green 50-chips clearly countable.
- The chip recognizer reported approximate inventory counts for both seats, with occlusion noted on some stacks.
- The blind/dealer button subagent reported dealer and small blind on the opponent side and big blind on the robot side.
- The held-card subagent read the visible held card as `3d`.
- The robot-behavior subagent described the hand as mid-action and not stuck.

## Notes
- I did not execute any robot actions.
- The opponent betting area is partially occluded, so that bet count is incomplete.
- The latest scene should be treated as still in progress rather than a settled decision point.
