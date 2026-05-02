# DexHoldem Perception Report

Run: `p5_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`

Current state: `s3`

## Summary

- Scene stability: unstable
- Turn detection: it is our turn
- Community cards: no readable face-up cards; the board shows five unreadable card backs
- Blind/dealer buttons: dealer and small blind on opponent side, big blind on robot side
- Robot behavior: hand is extended over the near player area and not yet at rest
- Held card: unreadable

## Subagent Evidence

- Scene stability agent: compared `s2/00_capture.jpg` and `s3/00_capture.jpg`, judged the scene unstable because the robot gripper has moved over the near table/card area.
- Turn detection agent: found the white "Your Turn" button near the robot seat.
- Community cards agent: reported five unreadable card backs in the board area.
- Blind button agent: reported dealer and small blind on opponent side, big blind on robot side.
- Robot behavior agent: reported the robot hand extended over the near player area and not in a rest pose.
- Held-card agent: reported the face-down card as unreadable.

## Reasoning Subagent

The reasoning subagent could not complete because its configured `inherit` model is not supported in this environment. No poker action was committed from that subagent.

## Perception Conclusion

The latest captured scene is not stable enough to treat as settled. The robot is still in an active, non-idle pose over the play area, so the safe interpretation is to wait for a cleaner settled frame before any downstream action decision.
