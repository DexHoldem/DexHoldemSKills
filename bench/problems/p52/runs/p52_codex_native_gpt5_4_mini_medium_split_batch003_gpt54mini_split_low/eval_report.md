# DexHoldem Perception Report

State: `s0`

## Merged Visual Findings

- The scene is visually settled in the static-frame sense, but the robot behavior subagent indicates the hand is still extended over the table and in progress.
- The white `Your Turn` button is visible near the bottom-left robot seat area, so it is our turn.
- Five community cards are visible, but none are readable from this capture.
- No robot-held hole card is safely identifiable.
- Dealer appears on the opponent side at the top-center; big blind is explicitly marked on the opponent side; small blind is a best guess at the robot seat.
- Both betting areas show the same visible chip mix in the capture: about 4 red `5` chips, 3 blue `10` chips, plus a partly occluded cluster with 1 green `50` chip and 2 brown `100` chips.

## Conservative State Judgment

I marked `scene_stable` as `false` in the structured summary because the robot behavior evidence suggests an in-progress hand posture, even though the stability subagent considered the single frame settled.

## Notes

- No robot actions were executed.
- Image interpretation stayed in subagents; the main agent only merged their outputs.
