# DexHoldem Perception Step

## Outcome
Perception completed for `s33/00_capture.jpg`. No robot action was executed.

## Merged Evidence
- Scene is unstable.
- It is our turn.
- Community cards: `Ts, 5h, 7d, Qs, Js`.
- Dealer button is on the opponent seat; opponent is small blind; robot is big blind.
- Current bets: robot `260`, opponent `265`.
- Robot inventory: `red=5, blue=8, green=0, brown=2`.
- Opponent inventory: `red=2, blue=5, green=1, brown=4`.
- Held robot card is unreadable.
- Robot behavior is still `acting`, with the hand extended over the upper-right/opponent side.

## Reasoning Check
The supported poker-action recommendation was `call` with low confidence. That recommendation is consistent with the merged state because:
- It is the robot's turn.
- `check` is not supported under the reported bet sizes.
- Hole cards are unavailable, so a conservative supported action is appropriate.

## Notes
- The reasoning agent required a supported model override; the visible `inherit` default was not usable in this environment.
- The report intentionally contains only perception and reasoning evidence. No executor or robot motion was triggered.
