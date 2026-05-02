# DexHoldem Perception Report

Run: `p58_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`

## Result

The current perception step is assembled from split visual subagents only. No robot action was executed.

## Key Observations

- Scene stability: unstable, because the robot hand is extended over the table and there is no prior frame to confirm completion.
- Turn: it is our turn, based on the visible white `Your Turn` button.
- Buttons: dealer is robot, small blind is robot, big blind is opponent.
- Community cards: `Jh Ac Ks 4c Kd`.
- Held card: no readable robot-held card is visible.
- Current bets:
  - Robot: 4 red `5` chips visible, with slight overlap uncertainty.
  - Opponent: 1 red `5` chip and 1 blue `10` chip visible, with partial occlusion uncertainty.

## Raw Evidence

All requested raw evidence files exist under `visual_raw/`.

## Notes

- The report intentionally does not claim more certainty than the subagents provided.
- No Texas Hold'em action reasoning was needed for this perception-only step, so the reasoning subagent was not invoked.
