# DexHoldem Perception Report

- Run: `p23_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`
- Source state: `s22`
- Capture: `s22/00_capture.jpg`

## Evidence

- Scene stability agent: unstable.
- Turn detection agent: yes, `Your Turn` button visible.
- Robot behavior agent: hand paused or mid-action over the table.
- Reasoning agent: keep the cached recovery state and do not mark the scene stable yet.

## Merged Result

- `loop_stage`: `to_recover`
- `intent`: `recover_cached_action`
- `current_action`: `recover_cached_action`
- `retry_count`: `1`
- `last_error`: `Previous intended motion was interrupted or did not reach the expected destination.`
- `scene_stable`: `false`
- `is_my_turn`: `true`
- `uncertain_fields`: `scene_stable`

## Raw Evidence

- `visual_raw/00_capture.jpg`
- `visual_raw/evidence.txt`

## Notes

- No robot action was executed.
- The scene was not marked stable because the robot arm remained extended over the table and the frame looked mid-action.
