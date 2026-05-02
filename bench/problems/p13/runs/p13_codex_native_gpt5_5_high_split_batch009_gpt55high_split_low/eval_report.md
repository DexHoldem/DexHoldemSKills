# Eval Report

Perception step completed for `s7` using split visual subagents.

## Evidence

- Scene stability: unstable; the robot arm is still over the table and the frame appears transient.
- Turn detection: it is our turn.
- Community cards: none visible.
- Current bets: no countable chips in either betting area.
- Blind/dealer assignment: dealer and small blind on the opponent seat; big blind on the robot seat.
- Held card: no readable held card visible.
- Robot behavior: hand extended over the right/central table area, not at rest.

## Missing Data

- Chip inventories could not be completed in time by the chip recognition subagent, so they are left unset in the summary.

## Output Verification

- `runs/p13_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_raw/` contains raw evidence files.
- `runs/p13_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_summary.json` was written.
- `runs/p13_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/eval_report.md` was written.
