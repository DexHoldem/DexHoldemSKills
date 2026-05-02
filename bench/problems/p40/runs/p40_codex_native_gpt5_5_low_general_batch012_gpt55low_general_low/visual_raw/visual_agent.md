Visual evidence merged from the visible subagents.

Stability pass:
- Unstable.
- Compared `s35/00_capture.jpg` and `s36/00_capture.jpg`.
- The robot hand and the visible player both changed position between captures.
- In the first image, the robot gripper is holding or occluding an upright 9-diamond card near the lower-right table area.
- In the second image, that card is lying flat near the lower center/right, while the robot gripper has moved above the table.
- The human player also tilts their head downward in the second image.

Table-state pass:
- A robot arm/hand is present and intrudes over the central/right table area.
- The scene appears to be a human-help or manual-reorganization case.
- Robot: black arm enters from the right, with the gripper over the middle-right betting/card area.
- Human/manual presence: a person is leaning over the table and looking down toward the layout.
- Community cards: multiple face-up board cards are visible across the center line, but the robot occludes part of the row.
- Chip zones: several chip stacks/clusters are visible in the lower/robot-side and upper/opponent-side zones, but the right/lower-right area is partly hidden by the robot body and arm.
- Buttons/markers visible: a yellow `BIG BLIND` button near the lower-right, a white `Your Turn` marker near the lower-left, and a white `DEALER` button near the upper-center.
- The state is visually blocked/unstable for reliable parsing until the robot hand and human clear the table.
