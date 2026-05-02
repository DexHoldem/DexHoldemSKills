# Eval Report

Current perception result for `s_current/00_capture.jpg`:

- Scene is unstable; the prior `put_down_card` sequence does not look fully settled.
- It is not the robot/player turn.
- No readable held card is visible.
- Five community-card positions are visible, all face-down and unreadable.
- My current bet area: 3 red `5` chips, 5 blue `10` chips, 0 green `50` chips, 0 brown `100` chips.
- Opponent bet area: 2 red `5` chips, 3 blue `10` chips, 1 green `50` chip, 0 brown `100` chips.
- Robot inventory: 5 red `5` chips, 5 blue `10` chips, 4 green `50` chips, 2 brown `100` chips.
- Opponent inventory: 4 red `5` chips, 5 blue `10` chips, 4 green `50` chips, 2 brown `100` chips.

Key issue:

- The robot behavior read indicates the returned hole card is lying face-down diagonally in the bottom robot inventory zone, overlapping chips and hiding part of the blue chip group. This is not a safe retryable miss and likely requires human help.
