# Visual Evidence

## Returned subagent evidence

- `scene_stability_agent`: compared current capture with the previous frame and concluded the scene is not settled; the robot arm is still extended and the layout changes between frames.
- `robot_behavior_agent`: the robot hand is holding a single card upright, not near rest, and the action is still in progress.
- `turn_detection_agent`: it is our turn.
- `blind_button_recognition_agent`: dealer is the opponent; opponent is small blind; robot is big blind.
- `community_cards_agent`: visible board is `Ts`, `Qh`, `7d`, `6s`, `Jc`.

## Inherited state used

- `action_sequence.json`: cached `loop_stage` was `atom_idle`.
- `s36/01_parsed_state.md`: prior chip inventory and current bet counts were reused as durable state.
