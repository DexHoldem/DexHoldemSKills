# Perception Report

Source image: `s36/00_capture.jpg`

## Outcome

The current table scene is parseable enough to identify the board orientation, turn indicator, dealer/big blind markers, and part of the community cards, but the right side is occluded by the robot arm so not every field is fully reliable.

## Evidence Summary

- The table is upright from the camera perspective, with the near rail at the bottom and the far rail at the top.
- A `Your Turn` marker is visible near the lower-left seating area.
- `DEALER` and `BIG BLIND` markers are visible.
- The robot arm is present on the right side and blocks part of the board/right-side betting area.
- Community cards that can be read confidently are `10♠`, `8♥`, and `9♠`.
- One red `7` is visible, but its suit is not clear.
- A bottom-center hole card is clearly `9♦`.
- The paired hole card next to it is not reliably readable.
- Chip stacks/scattered chips are visible, but there is no confidently readable central pot total.

## Uncertainties

- Small blind marker not clearly visible.
- Far-right community card is partially occluded and should not be trusted.
- Exact seat ownership and action order are not recoverable from this still frame alone.

## Notes

No robot actions were executed. This report merges only the returned visual evidence from the subagents.
