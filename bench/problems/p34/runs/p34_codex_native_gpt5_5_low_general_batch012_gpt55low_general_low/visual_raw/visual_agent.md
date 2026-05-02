Visual evidence for run `p34_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low`, state `s31`.

Source image:
- `s31/00_capture.jpg`

Findings from the visual subagent:
- Scene appears stable; no obvious motion blur or displaced cards/chips.
- `is_my_turn`: true. A white puck near the robot/player side reads "Your Turn".
- Community cards visible in the center row: `Qh`, `7d`, `6s`, `4c`.
- No fifth river card is visible.
- `my_chips`: visible but exact total is not supported because of overlap and camera obstruction.
- `opponent_chips`: visible but exact total is not supported because of distance/overlap.
- `my_current_bet`: unclear; chips are visible near the robot betting area, but committed bet cannot be separated confidently from stack/pot.
- `opponent_bet`: unclear; chips are visible near the opponent betting area, but the exact committed amount is not reliably readable.

Uncertainty / occlusion:
- Robot arm/camera housing occludes the right side of the table and part of the betting area.
- Chip denominations are partly readable, but stacked chips prevent a supported exact count.
- Face-down robot hole cards are not being re-identified from the image; the cached hole cards remain the source of truth for them.
