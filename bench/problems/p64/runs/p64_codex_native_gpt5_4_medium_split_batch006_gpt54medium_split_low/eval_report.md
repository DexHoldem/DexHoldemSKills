# DexHoldem Perception Report

Run: `p64_codex_native_gpt5_4_medium_split_batch006_gpt54medium_split_low`

## Result

- Latest frame: `s1`
- Scene stability: unstable / not yet settled
- Turn: robot/player turn
- Dealer: opponent
- Small blind: opponent
- Big blind: robot
- Community cards: `Kd Ks Ac As Jd`
- Robot held cards: unreadable
- Showdown: visible
- Likely outcome: robot win

## Evidence Summary

- The robot arm is still extended into the lower-right area, and the scene changed between `s0` and `s1`, so the latest frame should be treated as unstable.
- A visible `Your Turn` button indicates it is the robot/player turn.
- The dealer button is in front of the opponent seat, and the big blind button is in front of the robot seat.
- Five community cards are visible in the center row.
- The robot gripper is visible but not holding a readable hole card.
- Showdown is visible with both players’ hole cards face-up; the board and exposed cards favor a robot full house if the robot’s `K` read is correct.

## Chip Counts

- Robot inventory: `2x 5`, `2x 10`, `1x 50`, `3x 100`
- Opponent inventory: `3x 5`, `4x 10`, `2x 50`, `1x 100`
- Current bet, opponent: `1x 100`, `2x 10`, `3x 50`, `0x 5`, plus `1` uncertain overlapping chip
- Current bet, robot: `1x 100`, `2x 10`, `1x 50`, `2x 5`

## Constraints Followed

- No robot actions were executed.
- No image perception was done in the main agent.
- Only subagent evidence was merged into the final artifacts.
