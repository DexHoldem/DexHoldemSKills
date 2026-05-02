# DexHoldem Perception Report

Run: `p56_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low`

## Result

The current table read indicates the scene is not yet stable enough to trust for action execution, and it is not the robot/player turn.

## Perception Summary

- Community cards: `Kd`, `3s`, `3c`, `5d`, `Tc`
- Turn: not our turn
- Dealer / blinds: dealer `robot`, small blind `robot`, big blind `opponent`
- Current bet read:
  - robot: `green=1`, `brown=1`
  - opponent: `red=6`, `blue=5`
- Chip inventory: not available because the chip recognition agent timed out

## Evidence Notes

- The scene stability subagent flagged the capture as unstable because the robot arm is still extended and occluding part of the table.
- The turn-detection subagent reported that the physical turn button is on the left side of the table, not in front of the robot/player position.
- The community-card subagent read a completed board: `Kd 3s 3c 5d Tc`.
- The bet-recognition subagent found a small lower-area bet for the robot and a larger upper-area opponent bet.
- The blind/button subagent reported robot as dealer and small blind, opponent as big blind.
- The chip-recognition subagent did not return a usable inventory read before timeout.

## Notes

- No robot action was executed.
- All visual evidence was taken from the local capture and merged from subagent outputs only.
