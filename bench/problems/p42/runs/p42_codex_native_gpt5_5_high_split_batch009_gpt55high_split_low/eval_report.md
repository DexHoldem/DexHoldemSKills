# Eval Report

## Outcome

Perception evidence was collected from the visible subagents and merged into `visual_summary.json`.

## Evidence

- Scene stability: unstable, because the robot is still holding the 5♦ above the table.
- Turn ownership: it is our turn, based on the visible white `Your Turn` button.
- Community cards: five visible cards, read left to right as `Qs`, `8h`, `7d`, `6s`, `Ac?`.
- Current bets:
  - Robot/player: blue 10 = 1, green 50 = 1, brown 100 = 2, red 5 = 0.
  - Opponent: blue 10 = 4, green 50 = 0, brown 100 = 0, red 5 = 0.

## Merge Notes

- The fifth community card and some bet counts were partially occluded, so they are marked uncertain in the summary.
- No robot actions were executed.
