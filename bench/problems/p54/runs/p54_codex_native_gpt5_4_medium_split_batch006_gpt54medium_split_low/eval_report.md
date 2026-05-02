# DexHoldem Perception Report

State: `s0`

## Verdict

The scene is not stable enough to treat as settled, and it is not our turn.

## Evidence

- Scene stability: unstable because the robot hand is extended across the upper-right/board area and occludes part of the table.
- Turn detection: the white turn button is on the top/opponent side, so it is not our turn.
- Blind/dealer buttons: dealer and small blind are at the robot seat; big blind is at the opponent seat.
- Community cards: three face-up cards are visible, read as `3c`, `5h`, and `Tc`; two board positions remain face-down/unreadable.
- Chip inventory: robot side counts are `3x 5`, `2x 10`, `2x 50`, `2x 100`; opponent side counts are approximately `4x 5`, `5x 10`, `2x 50`, `5x 100`.
- Held cards: both left and right robot-held hole cards are unreadable in this frame.
- Robot behavior: the hand is still in progress over the upper-right area, but no obvious safety issue is visible.
- Showdown: not a clear showdown state, and there is no reliable win/lose evidence.

## Notes

- No robot actions were executed.
- Evidence was merged from the visible subagents only.
