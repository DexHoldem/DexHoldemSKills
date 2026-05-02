# DexHoldem Perception Report

- Output directory: `runs/p64_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low`
- Current state: `s1`
- Router result: `visual_parse`
- Poker-action reasoning required: `no`

## Evidence

- Raw capture copied to [`visual_raw/00_capture.jpg`](runs/p64_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low/visual_raw/00_capture.jpg)

## Merged Visual Evidence

- The latest frame appears settled overall; the robot/camera assembly is parked at the right edge.
- `is_my_turn` is visible as true from the white `Your Turn` indicator near the bottom-left robot seat area.
- A yellow `BIG BLIND` button is visible near the robot/player seat.
- Community cards, hole cards, and chip counts are present but not reliable enough for exact parsing from the available angle and occlusion.

## Decision

- This step is a visual parsing step only.
- Do not commit any poker action.
- Do not execute robot actions.
