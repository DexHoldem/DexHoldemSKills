# Perception Run Report

- Run: `p20_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low`
- Latest state: `s18`
- Output directory: `runs/p20_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low`

## Result

The scene is stable, but it is not the robot's turn to act. The board is still face-down, so there is no showdown state. The blind assignment is opponent as dealer/small blind and robot as big blind. Cached hole cards are `9d` and `5d`.

## Visual Evidence

- Community cards: none visible; all five board cards are face-down.
- Turn detection: not our turn.
- Scene stability: stable frame.
- Blind buttons: opponent is dealer and small blind; robot is big blind.
- Bets: robot-side bet total reported as 100; opponent-side bet total reported as 10.
- Robot behavior: hand is extended over the lower-right chip area and appears mid-action.
- Showdown: no clear win/loss or showdown evidence.

## Validation Notes

- No robot actions were executed.
- No poker action was requested or committed because turn detection indicates it is not the robot's turn.
- The bet-recognition result is partially occluded, so the totals should be treated as visual estimates rather than authoritative state transitions.
