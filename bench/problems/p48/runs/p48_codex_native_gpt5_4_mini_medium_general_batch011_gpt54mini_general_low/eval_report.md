# DexHoldem Perception Report

State: `s48`

## Result

- Scene stable: yes
- Turn: our turn
- Community cards: `Ts`, `Qh`, `7d`, `6s`, `Jc`
- Hole cards in parsed state: `9d`, `5d`

## Evidence Merged From Visual Subagents

- The current frame matches the previous frames closely. The table layout, board, chip placement, and seat markers are unchanged across `s48/00_capture.jpg`, `s47/00_capture.jpg`, and `s46/00_capture.jpg`.
- The only notable change is a small shift of the robot arm/camera on the right, which does not affect table state.
- The white `Your Turn` chip is visible near the lower-left seat area, supporting `is_my_turn = true`.
- The board is complete with five face-up community cards in the center row.
- Chips are distributed in seat-side inventory clusters, and no clearly isolated central pot is visible.

## Uncertainties

- The dealer button is not clearly visible.
- Small chip clusters near the action lane are ambiguous and may be either bets or inventory.
- Some board-edge / chip regions are partially occluded by the robot/camera assembly.

## Raw Evidence

- `runs/p48_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/visual_raw/evidence.txt`

## Verification

- Requested output files exist:
  - `runs/p48_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/visual_raw/evidence.txt`
  - `runs/p48_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/visual_summary.json`
  - `runs/p48_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/eval_report.md`

