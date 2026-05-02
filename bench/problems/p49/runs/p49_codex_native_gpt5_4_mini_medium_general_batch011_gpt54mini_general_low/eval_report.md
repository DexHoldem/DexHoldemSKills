# Eval Report

Current perception step completed from the latest capture.

## Merged Evidence

- The scene appears stable enough for perception.
- A `Your Turn` cue is visible, supporting `is_my_turn = true`.
- The board appears to show `Ts Qh 7d 6s Jc`.
- My hole cards appear to be `9d 5d`.
- Chip stacks are visible, but exact stack counts and bet totals are not reliably legible from this frame.
- A `BIG BLIND` button is visible, and no obvious scene inconsistency was reported by the visual subagents.

## Output Verification

- Raw evidence directory exists and contains real files.
- `visual_summary.json` was written.
- `eval_report.md` was written.

## Notes

- No robot actions were executed.
- No image perception was performed in the main agent; this report merges subagent evidence only.
