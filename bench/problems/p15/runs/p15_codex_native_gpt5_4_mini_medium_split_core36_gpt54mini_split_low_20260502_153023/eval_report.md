# Visual Perception Report

- Scene stability: unstable compared with `s9/00_capture.jpg`; the robot arm/gripper shifted between frames.
- Loop stage: `acting`, consistent with `action_sequence.json` and the visible in-progress hand motion.
- Turn marker: it is our turn.
- Blind/dealer: robot is big blind, opponent is small blind; dealer button is on the opponent side.
- Community board: no readable face-up community cards; omit from board output.
- Chips: robot inventory and lower-side bet area both read as 4x5, 4x10, 0x50, 0x100; opponent inventory and upper-side bet area are approximate and partly occluded.
- Showdown: not at showdown.

## Raw Evidence

- Robot hand is still moving into the lower-right player/card area and is not near rest.
- No held card is clearly visible in the hand.
- The scene includes the `Your Turn` marker near the robot side.
- The board area shows only unreadable/face-down-looking card backs, so no community ranks were reported.
