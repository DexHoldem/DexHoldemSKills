# Perception Report

## Outcome

- Scene stability: stable
- Turn: it is our turn
- Board: five community cards visible
- Hand result: win
- Robot action: not executed

## Key Evidence

- The white physical turn button is visible at the bottom-left and reads `Your Turn`.
- Five community cards are visible in the central row, with ranks reading as `K, K, A, A, J`; suits are uncertain.
- The showdown reader reports the robot hole cards as `K♠` and `2♠`, with the visible board making the robot ahead.
- The robot-hand area is occluded on the right, but the scene itself appears settled and not in motion.

## Ambiguities

- Dealer, small blind, and big blind assignment are not cleanly resolved from this frame alone.
- Bet-chip and inventory-chip counts are only partially countable and should be treated conservatively.

## Notes

- I used only the visible split subagents and merged their evidence.
- No robot actions were dispatched.
