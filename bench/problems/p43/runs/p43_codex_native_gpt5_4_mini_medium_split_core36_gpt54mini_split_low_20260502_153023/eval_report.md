# Eval Report

- `scene_stable`: false
- `loop_stage`: acting
- `is_my_turn`: true
- `blind`: big_blind
- `showdown_outcome`: not_showdown

Merged evidence:
- The scene is still moving; the robot hand is withdrawing from the lower-right chip area, so this is not yet settled.
- The button layout shows opponent dealer/small blind and robot big blind.
- The board is partially occluded; prior durable board state was carried forward for the summary.
- Chip and bet counts were merged from the subagents, with uncertainty preserved in `uncertain_fields`.
