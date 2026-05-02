# DexHoldem Perception Report

- Output directory: `runs/p8_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low`
- Current state: `s6`
- Capture: `s6/00_capture.jpg`

## Result

- `scene_stable`: true
- `is_my_turn`: true
- `loop_stage`: `preflop`
- `community_cards`: none visible
- `my_chips`: uncertain
- `opponent_chips`: uncertain
- `my_current_bet`: uncertain
- `opponent_bet`: uncertain

## Evidence

- One visual subagent reported a clearly visible `Your Turn` chip and no obvious instability in the table state.
- The second visual subagent agreed the scene is stable and my turn, and classified the stage as `preflop`.
- Both subagents marked chip and bet quantities as uncertain.

## Notes

- No robot actions were executed.
- Raw evidence files are present in `visual_raw/`.
