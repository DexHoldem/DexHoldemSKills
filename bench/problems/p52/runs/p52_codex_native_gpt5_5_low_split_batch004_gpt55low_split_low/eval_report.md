# DexHoldem Perception Report

Run: `p52_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low`

## Result

Partial perception completed from subagent evidence only.

## Summary

- `is_my_turn`: true, based on the visible white turn button.
- `scene_stable`: false/unstable in the evidence stream, because one agent could not access the expected capture image.
- `dealer_button`, `small_blind`, `big_blind`: unclear.
- `community_cards`: none readable from the provided evidence.
- `my_current_bet`: 4x5 chips and 4x10 chips.
- `opponent_bet`: 2x50 chips and 5x100 chips.
- `my_chips`: 5x5, 3x10, about 3x50, 2x100.
- `opponent_chips`: about 5x5, 5x10, 3x50, 5x100.
- `robot_held_card`: unreadable.

## Notes

- I did not execute any robot action.
- The visual evidence is internally inconsistent on capture availability: some subagents reported the image path as missing, while others returned usable observations from the current capture context.
- Uncertainty is highest for blind assignment and opponent chip counts because of occlusion.
