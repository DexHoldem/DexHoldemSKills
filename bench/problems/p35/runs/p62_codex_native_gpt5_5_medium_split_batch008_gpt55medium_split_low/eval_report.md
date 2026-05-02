# Eval Report

## Result

Perception step completed for `s1` with split visual evidence merged into the requested run directory.

## Evidence Summary

- `scene_stability_agent`: unstable; robot hand still extended over the table.
- `turn_detection_agent`: white turn button visible at the lower-left edge and labeled "Your Turn."
- `community_cards_agent`: three community cards read as `4c`, `As`, `Jd`.
- `bet_recognition_agent`: robot bet read as `1x10 + 1x100`; opponent bet read as `2x5 + 3x100`.
- `chip_recognition_agent`: robot inventory read as `1x5, 2x10, 1x50, 2x100`; opponent inventory read as approximately `5x5, 4x10, 3x50, 4x100`.

## Router / Action

No robot action was executed. The parsed state indicated `wait_for_opponent`, and the unstable scene means the frame should not be used to commit a physical action.

## Notes

- Raw evidence files were written under `runs/p62_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low/visual_raw/`.
- A dedicated reasoning subagent was not invoked because no `choose_poker_action` request was present.

