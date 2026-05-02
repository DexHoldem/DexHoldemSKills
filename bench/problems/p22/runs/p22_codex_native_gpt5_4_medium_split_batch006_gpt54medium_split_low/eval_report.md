# DexHoldem Perception Step

State: `s20`

## Result

- `scene_stable`: `false`
- `is_my_turn`: `true`
- `community_cards`: none visible
- `robot_motion`: still in progress
- recommended action: `wait`

## Visual Evidence

- The white turn button is visible near the robot seat at the bottom-left, so it is our turn.
- No shared community cards are visible.
- The robot hand is still extended over the robot-side chip area and has not returned to a settled pose.
- The scene is unstable because the robot arm moved substantially between frames and remains in motion.

## Bet Reads

The bet subagents did not agree on an exact count:

- One read saw the lower/robot betting lane as roughly `1x 5-chip` and `2x 10-chip`, with the upper lane not clearly countable.
- Another read saw the left betting area as `4x 5-chip` and the right betting area as `3x 10-chip`, with partial occlusion on the right.

Because of that disagreement, the bet fields are marked uncertain in the summary instead of being overcommitted.

## Files Written

- `visual_raw/s20_evidence.txt`
- `visual_summary.json`
