# Eval Report

State `s36` was perceptually assessed from `s36/00_capture.jpg` using the visible split visual subagents only. No robot action was executed.

## Outcome

- Scene stability: unstable.
- Turn ownership: it is our turn.
- Blind assignment: dealer/small blind at the opponent seat; robot is big blind.
- Community cards: 2 visible, read as `Qs`, unreadable, `8c`.
- Current bet areas:
  - Robot: 1 blue 10-chip and 2 brown 100-chips, with the blue chip slightly uncertain.
  - Opponent: 2 red 5-chips and 3 blue 10-chips.
- Chip inventories:
  - Robot: 4 red 5-chips, 3 blue 10-chips, 0 green 50-chips, 0 brown 100-chips visible.
  - Opponent: 2 red 5-chips and 4 blue 10-chips visible.
- Held card: no readable held hole card visible.
- Robot behavior: hand is extended over the lower-right board area and is not in a settled idle pose.

## Notes

- The scene is not stable enough to advance the perception pipeline as if the table were settled.
- The reasoning subagent was not invoked because no poker action was being committed in this step.
