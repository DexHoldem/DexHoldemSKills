# Eval Report

## Output Verification

- `visual_raw/` exists and contains real evidence files.
- `visual_summary.json` exists.
- `eval_report.md` exists.

## Merged Perception

The current frame at `s34/00_capture.jpg` shows a stable poker table scene with a major right-side occlusion from the robot/camera arm.

Key merged findings:
- `is_my_turn` is true.
- The visible turn marker says `Your Turn` near seat 6 in the bottom-left area.
- Community cards appear to be `10S, QH, 7D, 6S, 9D`, with the rightmost card partially occluded.
- Visible held cards include bottom-left/seat 6 showing `10S` and `QH`.
- Button/blind markers are visible: `DEALER`, `SMALL BLIND`, and `BIG BLIND`.
- Chip stacks and bet totals are present but low-confidence due to overlap and occlusion.
- No showdown or outcome cue is visible.

## Notes

- I did not execute any robot action.
- I did not rely on main-agent image perception; the summary was merged from the two visual subagents only.
- No Texas Hold'em action reasoning was required for this perception-only step.
