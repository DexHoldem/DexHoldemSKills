# Eval Report

Current state: `s23`

## Visual Evidence

- Turn detection: it is our turn.
- Community cards: 0 face-up; all five board positions are unreadable/face-down.
- Betting chips: robot current bet is blue=1; opponent current bet is red=3, blue=5, with partial uncertainty on the blue count.
- Blind buttons: dealer and small blind are opponent; big blind is robot.
- Scene stability: unstable, because the robot arm/toolhead is still over the table near the betting area.

## Perception Outcome

The run has enough evidence to confirm turn ownership and the current visible betting state, but the scene is not settled. I did not execute any robot action. I also did not invoke Texas Hold'em action reasoning because the scene-stability evidence is sufficient to mark the step as unsafe to continue from this frame alone.

## Evidence Files

- `visual_raw/turn_detection_agent.md`
- `visual_raw/community_cards_agent.md`
- `visual_raw/bet_recognition_agent.md`
- `visual_raw/blind_button_recognition_agent.md`
- `visual_raw/scene_stability_agent.md`

