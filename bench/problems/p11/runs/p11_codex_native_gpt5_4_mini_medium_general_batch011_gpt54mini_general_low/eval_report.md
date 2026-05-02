# DexHoldem Perception Report

## Result

The current capture at `s3/00_capture.jpg` is mostly stable and suitable for a perception read, with one caveat: the lower-right robot-side area is partially occluded by the hand.

## Merged Evidence

- The table layout is unchanged from the previous frame, and there is no visible motion blur.
- The robot hand is near idle on the right side.
- The scene uses the expected geometry: opponent at the top, robot/player at the bottom, community row in the middle.
- `Your Turn` is visible, so it is the robot's turn.
- `BIG BLIND` is visible near the lower-right/robot side.
- No face-up community cards are visible; the board area shows gray card backs.
- Hole cards are face-down or occluded and are not readable.
- Chip groups are visible on both sides, but the current bet areas cannot be separated reliably from inventory chips in this frame.

## Confidence

- High confidence: scene stability, turn indicator, blind marker, and absence of readable community cards.
- Medium confidence: robot pose and table geometry.
- Low confidence: chip/bet separation and any unreadable card or marker details.

## Files Written

- `runs/p11_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/visual_raw/visual_agent.md`
- `runs/p11_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/visual_summary.json`
- `runs/p11_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/eval_report.md`
