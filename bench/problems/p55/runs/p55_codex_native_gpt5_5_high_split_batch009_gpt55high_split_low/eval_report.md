# DexHoldem Perception Report

## Outcome
Perception step completed from subagent evidence. No robot action was executed.

## Verified Observations
- Scene stability: not stable enough to treat as settled; robot arm is still extended and occluding part of the table.
- Turn: not our turn.
- Community cards: `3s`, `3c`, `5d`, `Tc`.
- Buttons: dealer on robot, small blind on robot, big blind on opponent.
- Bet totals: robot `110`, opponent `70`.
- Robot-held hole card: none visible.

## Caveats
- The bet-recognition worker reported mild occlusion on the opponent side.
- The chip inventory worker did not return before timeout, so no inventory count is included here.
- The reasoning subagent could not be used in this environment because the `inherit` model is unsupported for that agent type on this account.

## Decision
Because it is not our turn, no poker action was routed or committed.
