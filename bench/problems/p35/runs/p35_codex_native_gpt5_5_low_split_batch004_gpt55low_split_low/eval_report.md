# Perception Report

## Outcome
The current frame in `s32` is not a clean settled win-state frame. The scene is still visually active, with the robot arm extended over the table, and the board shows only four community cards.

## Evidence
- Scene stability: unstable because the robot arm/end effector is still over the play area and occluding part of the table.
- Robot behavior: open/empty hand, extended over the upper-right betting/chip area, not in a rest pose.
- Showdown state: not showdown.
- Community cards: `Qh`, `7d`, `6s`, `4c`.
- Blind buttons: dealer and small blind on opponent; big blind on robot.
- Held cards: no visible held card in the gripper.
- Bets: robot current bet visible as green `x1`, blue `x1`, brown `x2`; opponent bet partially occluded but visibly present.
- Chip inventory: robot `red=5`, `blue=3`, `green=1`, `brown=1`; opponent `red=2`, `blue=5`, `green=2`, `brown=2`.

## Interpretation
The frame does not show the clear post-hand collection state that would justify committing a collect-winnings robot action from perception alone. It looks like an in-hand state with the robot still physically engaged above the table.

## Decision
No robot action was executed. The perception result should be treated as an unstable, non-showdown frame with incomplete collection evidence.
