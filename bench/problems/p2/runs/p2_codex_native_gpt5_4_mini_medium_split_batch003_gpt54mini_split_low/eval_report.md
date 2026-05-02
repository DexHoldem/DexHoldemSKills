# DexHoldem Perception Report

## Result

- State: `s0`
- Scene stability: stable
- Turn: not our turn
- Community cards: none visible
- Held card: no readable held card visible
- Chip inventory: unresolved

## Evidence

- The scene stability agent judged the frame stable, with no visible motion blur or ongoing transfer.
- The turn-detection agent placed the white turn button on the opponent/top side of the table, so it is not our turn.
- The robot-behavior agent described the dexterous hand as extended over the upper-right table area, not holding a card or chips, and not showing damage or pinning.
- The community-card agent reported no community cards visible.
- The blind-button agent reported the opponent as dealer and small blind, with the robot as big blind.
- The held-card agent reported no readable held card visible.
- The chip-recognition agent did not return before timeout, so chip inventory could not be merged safely.

## Notes

- No robot actions were executed.
- No image perception was performed in the main agent; the result is a merge of subagent evidence only.
- The output directory used is exactly `runs/p2_codex_native_gpt5_4_mini_medium_split_batch003_gpt54mini_split_low`.
