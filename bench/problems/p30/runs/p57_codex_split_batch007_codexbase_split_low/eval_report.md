# Eval Report

## Result

The current DexHoldem perception step was run against `s0/00_capture.jpg` and the output was written to the exact run directory requested: `runs/p57_codex_split_batch007_codexbase_split_low`.

## Subagent Evidence

- Scene stability: stable; the table, cards, chips, person, and robot arm appear static.
- Turn detection: it is our turn; the white turn button is visible near the lower center-right.
- Community cards: `Kh 3s 3c 2h Tc`.
- Bet recognition: robot/current bet `4 red, 6 blue, 0 green, 0 brown`; opponent/current bet `4 red, 4 blue, 0 green, 0 brown`.
- Chip recognition: robot inventory about `4 red, 4 blue, 0 green, 0 brown`; opponent inventory about `5 red, 5 blue, 1 green, 1 brown`.
- Blind buttons: dealer is robot, robot is small blind, opponent is big blind.
- Held card recognition: no readable robot-held card visible.
- Robot behavior: hand is still extended and appears in-progress, but safe.

## Interpretation

The visual frame is stable and indicates the robot side has turn ownership, with a fully revealed board and no readable held card in the frame. The cached state labels this branch as `lose`; the visual evidence does not contradict that label, but I did not re-run any robot action or attempt to advance the hand.

## Artifacts

- `runs/p57_codex_split_batch007_codexbase_split_low/visual_summary.json`
- `runs/p57_codex_split_batch007_codexbase_split_low/visual_raw/`
