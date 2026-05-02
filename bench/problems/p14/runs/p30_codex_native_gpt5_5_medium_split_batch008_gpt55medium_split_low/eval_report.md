# DexHoldem Perception Report

## Result
The current capture at `s28/00_capture.jpg` appears stable, and it is the robot's turn.

## Evidence
- Scene stability agent: the frame shows no visible active motion blur and is settled enough to continue.
- Turn detection agent: the "Your Turn" button is visible, so it is our turn.
- Blind/button agent: dealer and small blind are on the opponent; big blind is the robot.
- Community cards agent: four community cards are visible left to right as `Qh`, `7d`, `6s`, `7c`.
- Bet recognition agent: robot current bet is `1x5`, `2x10`, `1x50`, `2x100`; opponent current bet is `3x5`, `1x10`, `1x100`.
- Chip recognition agent: robot inventory is `7x5`, `7x10`, `2x50`, `4x100`; opponent inventory is `2x5`, `7x10`, `3x50`, `4x100`.
- Held-card agent: no robot-held card is visibly readable.
- Robot behavior agent: the hand is hovering over the right side of the table, not clearly holding a card or chips, and no immediate safety issue is visible.

## Raw Evidence
- `runs/p30_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low/visual_raw/s28_00_capture.jpg`

## Notes
- The requested reasoning subagent could not be started because the agent thread limit was reached.
- No robot actions were executed.
