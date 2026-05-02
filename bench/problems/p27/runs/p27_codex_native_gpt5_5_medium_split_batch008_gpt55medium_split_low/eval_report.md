# DexHoldem Perception Report

Latest capture: `s22/00_capture.jpg`

## Visual Findings

- Scene stability: unstable. The robot hand moved into a new extended pose over the right side of the table, and a human hand/arm remains near the chips.
- Turn detection: it is not our turn. The white turn button is on the upper/opponent side of the table, left of center.
- Robot behavior: no clear motion blur proves the robot is still moving, but the hand is not in a rest pose and is close to a human hand/arm, so the scene needs caution.

## Outcome

- No robot action executed.
- Recommended state: wait for the next stable capture and re-evaluate turn ownership.
