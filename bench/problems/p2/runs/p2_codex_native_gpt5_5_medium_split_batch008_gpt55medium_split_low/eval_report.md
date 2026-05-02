# Perception Report

State `s0` was inspected from the existing capture at `s0/00_capture.jpg` using split visual subagents only.

## Findings
- Scene is stable enough to continue.
- It is not the robot/player turn.
- No community cards are readable; the board appears face-down.
- No held card is visibly readable from the robot gripper.
- Blind assignment is opponent dealer, opponent small blind, robot big blind.
- Robot/player current bet could not be counted with confidence.
- Opponent current bet was partially readable: red 6, blue 5, green 5, brown 6.
- Robot inventory counts were read as red 6, blue 6, green 3, brown 4.
- Opponent inventory counts were read as red 6, blue 5, green 4, brown 5.
- Robot hand is extended/hovering over the right side of the table, but no object is visibly held and no safety issue is apparent.
- This is not a showdown state.

## Notes
- The summary is conservative where the image was occluded or cluttered.
- No robot action was executed.
- Raw evidence files were written under `visual_raw/`.
