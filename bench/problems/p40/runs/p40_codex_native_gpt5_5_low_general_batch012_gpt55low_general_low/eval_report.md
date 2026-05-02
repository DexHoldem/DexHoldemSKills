# DexHoldem Perception Report

Run: `p40_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low`

## Outcome

The current scene is unstable and visually blocked for reliable perception.

## Evidence

- Compared `s35/00_capture.jpg` and `s36/00_capture.jpg`.
- The robot hand and visible player changed position between captures.
- The robot gripper is still over the live table area and is interacting with or occluding a card.
- A human is leaning over the table, which supports the manual-reorganization interpretation.

## Visible Table Cues

- Community cards are visible across the center line, but part of the row is occluded by the robot.
- Several chip stacks or clusters are visible in both robot-side and opponent-side zones.
- A yellow `BIG BLIND` button is visible near the lower-right.
- A white `Your Turn` marker is visible near the lower-left.
- A white `DEALER` button is visible near the upper-center.

## Conclusion

The scene should be treated as unstable and blocked until the robot hand and human clear the table enough for reliable parsing.
