# DexHoldem Perception Report

- Latest state: `s30`
- Scene stability: stable
- Turn: our turn
- Board: `8h 7d 6s 7c`
- Blind assignment: dealer/small blind on opponent, big blind on robot
- Held hole card: not readable

## Visual Evidence

The visual subagents agree that the table is settled enough to continue. The turn button is reported on our side, and the board cards are visible as a four-card run: `8h`, `7d`, `6s`, `7c`.

The hand pose subagent says the robot hand is hovering over the table rather than clearly holding a card or chip. Bet and inventory counts are partially occluded and should be treated as approximate.

## Notes

- I did not execute any robot action.
- I did not use main-agent image perception; only subagent evidence was merged.
- Bet counts contain ambiguity around white chips and partial occlusion, so downstream routing should treat the counts as approximate.
