# Perception Step Report

Current state: `s39`

## Merged Evidence
- Scene is stable enough to continue.
- It is our turn according to the white physical turn button.
- Dealer button is on the opponent; opponent is small blind and robot is big blind.
- Community board shows `10s`, `8h`, `7d`, `6s`, and a fifth card that is partially obscured.
- Robot hole cards remain consistent with the cache: `9d`, `5d`.
- Robot inventory is approximately `4x 5`, `5x 10`, `1x 50`, `2x 100`.
- Opponent inventory is approximately `2x 5`, `3x 10`, `3x 50`, `2x 100`.
- Robot-side bet area shows `4x 5`.
- Opponent-side bet area shows `2x 10`, `1x 50`, `2x 100`.
- Robot hand is still in collect-winnings motion and appears safe; no robot action was executed.
- The showdown-outcome agent later indicated this is a showdown scene, but the opponent hole cards were not readable enough to confirm win/loss, so the outcome remains unresolved.

## Notes
- The showdown-outcome subagent recommended `show_hand` as the loop-stage label.
- This step only merged visual evidence; it did not command any robot action.
