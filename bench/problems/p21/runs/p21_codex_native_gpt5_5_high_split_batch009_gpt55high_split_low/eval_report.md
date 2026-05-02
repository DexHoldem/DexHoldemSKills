# DexHoldem Perception Report

Run: `p21_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low`

Latest state: `s18`

## Summary

The current scene is stable enough to continue. The robot is not taking a turn, the robot-held card is readable as `5d`, the community row has no face-up cards, and both current bet areas are empty.

## Evidence

- Scene stability: stable on `s18` compared with `s17`; the card placement appears settled.
- Turn: not our turn; the white turn button is visible near seat 6 on the lower-left side.
- Robot behavior: the hand is still extended over the lower-right card/chip area, but no failure or human-help issue is visible.
- Held card: `5d`.
- Community cards: none face-up; five face-down cards are visible in the shared row.
- Dealer / blinds: dealer and small blind are opponent; big blind is robot.
- Current bets: zero in both betting areas.
- Inventory chips:
  - Robot: `5x7`, `10x5`, `50x3`, `100x1`
  - Opponent: `5x4`, `10x5`, `50x4`, `100x6`

## Outputs

- Raw evidence: `runs/p21_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_raw/s18_00_capture.jpg`
- Summary JSON: `runs/p21_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_summary.json`

## Notes

- No robot actions were executed.
- The report is based on subagent evidence only.
