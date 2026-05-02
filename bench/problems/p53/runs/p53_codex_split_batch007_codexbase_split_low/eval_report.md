# DexHoldem Perception Report

State: `s0`

## Merged Evidence

- Scene stability: stable enough to continue.
- Turn detection: it is our turn.
- Blind/dealer assignment: robot is dealer and small blind at seat 6; opponent is big blind at seat 5.
- Community cards: 3 visible cards were readable as `3c`, `4h`, `Ts`; two earlier positions were unreadable face-down cards.
- Hole cards: no robot-held hole card was visibly readable.
- Bets: robot side showed `3 red` + `2 blue`; opponent side showed `4 red` + `6 blue`.
- Inventory chips: robot had `2 blue`, `3 red`, `3 green`, `2 brown`; opponent had `5 blue`, `4 red`, `3 green`, `3 brown`.
- Robot behavior: arm was extended over the table, mid-action, with no obvious safety issue or recovery need.

## Outcome

Perception data was collected successfully from the split visual subagents. No robot action was executed.

## Caveats

- Community-card positions 1 and 2 were unreadable.
- Opponent-side bet and inventory counts had minor occlusion uncertainty.
- Robot behavior evidence indicates motion in progress, so later action routing should recheck stability if a commit is needed.
