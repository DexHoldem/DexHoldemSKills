# Eval Report

Current state: `s46`

Perception result:
- `scene_stable`: true
- `is_my_turn`: true
- `loop_stage`: `acting`

Merged visual evidence:
- The scene is visually stable according to the stability reader.
- The robot arm is still extended over the right-center betting area, which supports `acting`/motion-in-progress rather than a completed rest pose.
- The white turn button is clearly visible, so this is our turn from the turn marker.
- Five community cards are visible: `10s, 8d, 7d, 6s, 7c`.
- The held card is not readable from the gripper frame.
- Dealer/small blind markers are unclear; a `BIG BLIND` puck is visible near the lower-right area.
- Bet and inventory chip counts are approximate and partially occluded.

Router implication:
- Conservative outcome is `wait_for_motion_completion`.
- No robot action was executed.

Uncertainty:
- The scene stability agent only had a single frame, so its stability judgment is based on visual stillness rather than a before/after comparison.
- Bet and chip counts are approximate due to occlusion.
