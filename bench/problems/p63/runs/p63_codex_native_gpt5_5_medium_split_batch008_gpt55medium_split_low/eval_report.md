# Eval Report

## Outcome

Perception pass completed from the local capture in `s0/00_capture.jpg`.

## Merged Visual Evidence

- Scene is stable.
- It is our turn.
- Five community cards are visible: Kh, Ks, 7s, As, Jh.
- Current bets were read as:
  - my bet: red 3, blue 2, green 2, brown 2
  - opponent bet: red 0, blue 2, green 3, brown 1
- Chip inventory was read as:
  - robot: 2 red 5-chips, 2 blue 10-chips, about 2 green 50-chips, about 3 brown 100-chips
  - opponent: about 4 red 5-chips, 1 blue 10-chip, about 3 green 50-chips, about 2 brown 100-chips

## Notes

- Evidence was merged only from scoped visual subagents.
- No robot actions were executed.
- The current hand state in the local sequence is already marked `win / collect_winnings`, so this pass did not require poker-action execution.
