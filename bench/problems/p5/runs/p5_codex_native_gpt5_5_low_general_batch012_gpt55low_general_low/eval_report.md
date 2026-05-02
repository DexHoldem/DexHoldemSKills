# DexHoldem Perception Report

Run: `p5_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low`
Step: `view_left_hole_card`
Intent: `pick_card`

## Result

Perception evidence was collected from the visible visual subagents and merged into the run artifacts. The scene shows the poker table with face-down community cards, face-down hole cards, visible blind markers, and partial occlusion from the robot hardware.

## Stability

The sequence is not fully stable. Prior frames show meaningful robot-arm movement, and the latest view still has lower-table occlusion around the hero cards/chips.

## Outputs

- `runs/p5_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low/visual_raw/visual_agent.md`
- `runs/p5_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low/visual_summary.json`
- `runs/p5_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low/eval_report.md`

## Constraints

- No robot actions were executed.
- No image perception was performed in the main agent.
