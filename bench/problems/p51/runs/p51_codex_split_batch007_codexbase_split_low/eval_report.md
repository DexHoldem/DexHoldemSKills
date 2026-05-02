# DexHoldem Perception Report

## Result

Wait. The current frame `s52/00_capture.jpg` is not stable enough for a downstream action decision.

## Merged Evidence

- Scene stability: unstable compared with `s51/00_capture.jpg`.
- Turn detection: it is our turn.
- Community cards: `T♠`, `Q♥`, `7♦`, plus a fourth card that is occluded/unreadable.
- Blind buttons: dealer is on the opponent seat, so opponent is small blind and robot is big blind.
- Bets: lower robot-side bet area shows about three blue 10-chips; opponent bet area shows about two red 5-chips and about four blue 10-chips.
- Chip inventory: both sides appear to have roughly 4 red 5-chips and 4 blue 10-chips, with occlusions limiting precision.
- Held cards: no readable robot-held card is visible.
- Robot behavior: the robot hand is mid-action over the lower-middle betting area and not near rest pose.

## Decision

Do not execute robot actions from this perception step. The robot arm is still moving, so the correct next behavior is to wait for another capture and re-evaluate once the scene settles.
