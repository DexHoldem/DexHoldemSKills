# DexHoldem Perception Step

- State: `s21`
- Loop stage: `to_recover`
- Frame used: `s21/00_capture.jpg`

## Merged evidence

- Turn: it is the robot/player turn.
- Scene stability: unstable; the robot arm is still extended and the scene appears mid-action.
- Community cards: unknown from this frame.
- Inventory: partial read only. Robot/player inventory visible at about 4 red 5-chips and 1 blue 10-chip; opponent inventory not countable.
- Blind buttons: unclear; dealer/small blind/big blind could not be verified.
- Bets: robot/player bet is 5 red + 1 blue; opponent bet is 0 visible.

## Result

This step should remain in the recovery branch rather than advancing to a new poker action. The visual evidence supports `recover_cached_action`, and the scene is not stable enough to treat the hand as complete.
