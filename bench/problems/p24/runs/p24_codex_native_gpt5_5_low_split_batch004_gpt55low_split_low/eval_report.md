# DexHoldem Perception Step

- State: `s21`
- Outcome: do not continue yet
- Reason: the visual subagents agree the robot hand is still extended over the lower chip area and the chip-push atom is still in progress, so the scene is unstable.
- Turn state: it is our turn

## Evidence

- `scene_stability_agent`: unstable; compared `s21/00_capture.jpg` with the prior state summary and judged the scene not yet settled.
- `robot_behavior_agent`: hand is mid chip-push, not near rest pose, no held chips/cards visible, no human-help concern.
- `turn_detection_agent`: the small white turn button is visible, and it is our turn.

## Decision

- Final perception result: wait for another capture.
- No robot action was executed.
