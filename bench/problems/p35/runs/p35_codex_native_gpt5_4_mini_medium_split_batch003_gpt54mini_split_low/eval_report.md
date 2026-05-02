# Eval Report

## Outcome

Perception step completed for `s32` using only specialized visual subagents. No robot action was executed.

## Merged Evidence

- Scene stability: stable.
- Turn state: it is our turn.
- Blind/button state: robot is big blind; opponent is dealer.
- Community cards: `8h, 7d, 6s, 7c`.
- Current bets:
  - Near-side / robot: `4 red, 4 blue, 1 green, 1 brown`.
  - Far-side / opponent: `3 red, 4 blue, 1 green, 1 brown`, with some occlusion uncertainty.
- Chip inventory:
  - Robot: `4 red, 6 blue, 1 green, 2 brown`.
  - Opponent: `3 red, 5 blue, 1 green, 1 brown`.

## Confidence

The turn, stability, and blind-button readings are high confidence. The bet and chip counts are slightly lower confidence because the right-edge stacks are partially occluded.

## Files Written

- `visual_summary.json`
- `visual_raw/`

