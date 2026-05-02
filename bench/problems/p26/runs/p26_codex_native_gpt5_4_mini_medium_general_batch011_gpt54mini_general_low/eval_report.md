# Evaluation Report

Current perception step: `recover_cached_action` for `p26`.

## Outcome
- The scene is stable enough to continue the perception flow.
- No robot motion is visibly in progress.
- Visual evidence does not support executing a robot action here; this step is perception-only.

## Merged Evidence
- The current capture is `s23/00_capture.jpg`.
- The robot arm and camera body are in essentially the same pose as the previous frame, with no visible blur or movement.
- The right side of the table remains heavily occluded.
- The blinds/button assignment appears consistent with the robot as big blind and the opponent as dealer/small blind.
- No readable held card is visible in the current frame.
- Five center cards are visible, but they appear face-down and unreadable.
- Chip clusters in the central lanes are present, but exact bet counts are not safely separable from inventory chips in this frame.

## Files Written
- `visual_raw/visual_agent.md`
- `visual_summary.json`
- `eval_report.md`

## Notes
- The raw evidence file is present on disk and contains merged outputs from both visual subagents.
- The current frame is suitable for the next perception decision, but not for a precise chip or card parse on the occluded right side.
