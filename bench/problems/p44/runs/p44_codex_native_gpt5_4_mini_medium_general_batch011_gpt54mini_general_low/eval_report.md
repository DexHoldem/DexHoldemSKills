# DexHoldem Perception Report

- Run: `p44_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low`
- State: `s41`
- Source capture: `s41/00_capture.jpg`

## Summary

The scene appears stable in the captured frame, and the table is likely at the user's turn. The most reliable visible cue is a `Your Turn` disc near seat 6.

## Observations

- Community cards are visible on the board.
- Readable cards include `10♣` and `9♦`.
- A third board card is partially visible but not fully readable because the robot arm blocks part of the table.
- Held cards are not reliably visible.
- Chip stacks are visible around seats 5 and 6.
- No unambiguous dealer/button marker is visible.

## Confidence and Limits

- Confidence is high that the capture shows the user's turn.
- Confidence is moderate that at least three community cards are on the table.
- Confidence is low for held-card identity, bet sizing, and chip counts because the robot arm occludes the important regions.

## Evidence

- `visual_raw/visual_agent.md`
- `visual_summary.json`
