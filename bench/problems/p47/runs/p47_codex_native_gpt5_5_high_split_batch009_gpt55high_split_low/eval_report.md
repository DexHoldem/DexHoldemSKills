# DexHoldem Perception Report

Latest state: `s46`

Summary:
- Turn button is visible and the subagent judged it is our turn.
- Scene stability is not settled; the robot gripper is still extended over the table area.
- Blind buttons are assigned with dealer and small blind on the opponent side and big blind on the robot side.
- Community board is read as `Qs, Qh, 7d, Qc, 7c`.
- Robot-held hole card was not identified as being held in the gripper.
- Robot behavior indicates an active reach/positioning step with no visible collision or dropped object.
- Bet recognition saw robot/player bet `blue 10 x1` and `green 50 x1`, while opponent bet `red 5 x4` and `blue 10 x2`, with one partially occluded chip possibly present on the robot/player side.
- Chip inventory was read as robot/player `red 8 blue 3 green 3 brown 5` and opponent `red 4 blue 5 green 4 brown 3`, with green and brown counts least certain.
- Showdown evidence suggests the hand is likely at showdown and may be a tie, but the exact winner is not certain from this frame.

Decision:
- Perception only. No robot action executed.
- The frame should be treated as visually informative but still in-progress because the robot pose is active and the scene-stability subagent marked it unstable.
