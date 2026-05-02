# DexHoldem Perception Step

Current state: `s41`

## Result

The perception step indicates the scene is not stable yet, even though it is the robot's turn.

## Evidence

- `scene_stability_agent.md`: the robot arm/hand moved significantly and occludes the board; scene is unstable.
- `turn_detection_agent.md`: the "Your Turn" button is visible; it is our turn.
- `community_cards_agent.md`: four community cards are visible; `10s` and `9d` are readable, two cards remain occluded.
- `bet_recognition_agent.md`: bet estimates were recorded for the top and bottom areas, but occlusion reduces confidence.
- `chip_recognition_agent.md`: approximate chip inventory counts were recorded for both sides, but confidence is low.
- `robot_behavior_agent.md`: the arm is still in progress and extended over the table; no obvious unsafe or failed recovery state is visible.

## Router-Level Interpretation

The current loop stage is `acting`, so the router would wait for motion to settle before re-parsing or advancing. No poker action was selected or executed.

## Files Written

- `visual_raw/scene_stability_agent.md`
- `visual_raw/turn_detection_agent.md`
- `visual_raw/community_cards_agent.md`
- `visual_raw/bet_recognition_agent.md`
- `visual_raw/chip_recognition_agent.md`
- `visual_raw/robot_behavior_agent.md`
- `visual_summary.json`
