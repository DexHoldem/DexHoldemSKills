# DexHoldem Perception Step

Source capture: `s18/00_capture.jpg`

## Outcome

- Scene is stable enough to continue.
- Robot hand is still active over the lower-right player area and not in a rest pose.
- It is not the robot/player turn.

## Evidence

- `scene_stability_agent`: the table, cards, chips, and robot hand are sharp and stationary with no visible motion blur or blocking instability.
- `robot_behavior_agent`: the robot hand is extended near the face-down hole cards and nearby chips, with the gripper appearing empty and the manipulation potentially still in progress.
- `turn_detection_agent`: the visible white `Your Turn` indicator is located near the lower-left seat area, not at the robot/player area.

## Notes

- No robot actions were executed.
- No visual perception was performed in the main agent; this report merges only subagent evidence.
