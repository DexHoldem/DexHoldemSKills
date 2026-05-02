# DexHoldem Perception Report

- Run: `p18_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low`
- State: `s18`
- Turn: yes
- Scene stability: unstable
- Showdown: no

## Merge

The visual subagents agree that the current capture shows an in-hand action state, not showdown. The robot/player turn is visible, but the scene is still partially occluded by the robot arm, so I did not treat the frame as fully settled.

## Visual Findings

- Community cards are not readable; the board appears to show only face-down card backs.
- Dealer button is on the opponent side.
- Small blind is the opponent; big blind is the robot.
- Robot-held card is present but face-down and unreadable.
- Robot inventory chips were counted as red 5 = 6, blue 10 = 4, green 50 = 4, brown 100 = 2, with some occlusion on the right-side stack group.
- Opponent inventory chips were counted as red 5 = 3, blue 10 = 5, green 50 = 3, brown 100 = 6.
- Robot behavior shows the hand extended over the lower-right player area near chips/cards, with no obvious collision or failure evidence.

## Output Verification

- Raw evidence directory contains real files under `visual_raw/`.
- `visual_summary.json` written.
- `eval_report.md` written.
