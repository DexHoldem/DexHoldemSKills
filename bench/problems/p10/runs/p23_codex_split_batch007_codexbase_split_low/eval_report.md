# DexHoldem Perception Report

- Run: `p23_codex_split_batch007_codexbase_split_low`
- State: `s22`
- Output directory: `runs/p23_codex_split_batch007_codexbase_split_low`

## Summary

The scene is stable and it is our turn. No community cards are visible. The robot hand is extended over the table in an in-progress reach/placement posture, but no readable hole card is visible. Showdown is not supported by the frame.

## Visual Evidence

- Scene stability: stable from the latest capture.
- Turn detection: the white turn button is visible near the lower-left area of the table, so it is our turn.
- Community cards: none visible.
- Blind/button assignment: best-effort identification says dealer/small blind are on the robot side and big blind is on the opponent side, but this is uncertain because no separate blind puck is clearly visible.
- Current bets: robot red 5 x3 and blue 10 x4; opponent red 5 x4 and blue 10 x4.
- Inventory: robot red 5 x3 and blue 10 x4; opponent red 5 x4 and blue 10 x4. Several chips are partially occluded, so counts may be off by a small amount.
- Held card: no readable robot-held hole card.
- Robot behavior: hand is hovering low above the chip area, still in progress, and appears safe.
- Showdown: not decidable from this frame.

## Notes

- No robot actions were executed.
- No poker action reasoning was required for this perception-only step.
