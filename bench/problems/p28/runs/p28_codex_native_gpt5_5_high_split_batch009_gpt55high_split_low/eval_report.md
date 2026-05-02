# Evaluation Report

Current capture: `s24/00_capture.jpg`

## Visual Evidence

- Scene stability: unstable. The robot arm/end effector is still extended over the table and is occluding the play area.
- Robot behavior: active/paused manipulation pose, not at rest; gripper appears empty; no clear recovery condition.
- Turn detection: it is our turn; the white `Your Turn` button is visible and unobstructed.
- Community cards: two readable face-up cards are visible, `7d` and `6c`; the remaining positions are unreadable or occluded.
- Blind/dealer assignment: dealer and small blind are on the opponent side; big blind is on the robot side.
- Bet counts: robot side shows 1 blue 10-chip; opponent side shows 2 green 50-chips and 1 brown 100-chip, with some occlusion.

## Perception Result

The step should remain in a wait/stable-observation state. The frame is not stable enough to advance based on robot motion, even though the turn button indicates it is our turn.

## Output Verification

- `runs/p28_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_raw/` contains raw evidence files.
- `runs/p28_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_summary.json` exists.
- `runs/p28_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/eval_report.md` exists.
