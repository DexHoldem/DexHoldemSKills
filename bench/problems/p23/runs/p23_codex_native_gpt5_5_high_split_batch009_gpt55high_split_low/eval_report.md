# Perception Step Report

- Capture analyzed: `s22/00_capture.jpg`
- Output directory: `runs/p23_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low`

## Merged Evidence

- `is_my_turn`: yes
- `scene_stable`: no
- `community_cards`: 0 visible
- `dealer_button`: opponent
- `small_blind`: opponent
- `big_blind`: robot

## Reasoning Check

- The reasoning subagent was asked to validate a poker action recommendation from the merged evidence.
- It concluded that no action should be committed yet because the scene is likely unstable and the chip/card area is occluded.

## Notes

- No robot action was executed.
- Raw evidence files were written under `visual_raw/` for the individual subagent outputs.
