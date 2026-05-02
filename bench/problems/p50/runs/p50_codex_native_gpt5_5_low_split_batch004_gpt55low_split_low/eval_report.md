# Eval Report

Perception-only pass for `s50`.

## Outcome

The scene is not stable enough to advance the perception loop into an action decision. The robot hand is still extended over the chip area, so this frame should be treated as `acting` rather than settled.

## Visual Evidence

- Turn detection: it is our turn.
- Scene stability: unstable.
- Community cards: `Qs 8h 7d 6s Jc`.
- Blind assignment: dealer/small blind is on the opponent side; big blind is the robot.
- Current bets:
  - robot/player: `10x1, 50x2, 100x4`
  - opponent: `5x2, 10x4, 50x2, 100x5`
- Inventory counts:
  - robot/player: about `5x8, 10x4, 50x3, 100x7`
  - opponent: about `5x3, 10x5, 50x4, 100x4`
- Held card recognition: no readable held card visible.
- Robot behavior: hand is actively down in the chip area; no clear failure or human-help condition.

## Interpretation

This is a valid perception step result, but not a stable hand state. The right next move is to wait for a settled capture before any action reasoning or robot command path is considered.
