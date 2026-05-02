# DexHoldem Perception Eval Report

Run: `p3_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`

## Result

The perception step was completed from visual subagent evidence only.

## Merged Findings

- The scene is stable.
- It is our turn.
- No readable community cards are face up.
- No robot-held card is visible.
- Dealer and small blind are on the opponent side; big blind is at the robot seat.
- Inventory counts and current bets were extracted from the visual agents and written to `visual_summary.json`.
- The robot hand is extended over the table but appears safe and not holding cards or chips.

## Notes

- Main-agent image inspection was not used.
- No robot actions were executed.
- Visual evidence was preserved in `visual_raw/` as requested.
