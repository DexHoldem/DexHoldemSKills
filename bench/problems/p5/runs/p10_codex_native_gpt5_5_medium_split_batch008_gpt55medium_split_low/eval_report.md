# DexHoldem Perception Run Report

Run: `p10_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`

## Result

Visual evidence was collected from scoped subagents and merged into a summary artifact.

## What Was Observed

- No readable face-up community cards were visible.
- Button assignment was readable: dealer and small blind on the opponent, big blind on the robot.
- The turn indicator said it is our turn.
- The scene was not stable enough to treat as settled.
- The robot hand was extended over the table and not visibly holding a card.
- Chip inventory was estimated from the image with minor overlap uncertainty.

## Outputs

- `visual_raw/` contains one evidence file per visual subagent.
- `visual_summary.json` contains the merged perception result.

## Caveats

- `scene_stable` is an inference from the scene evidence, not a direct robot state flag.
- Chip counts are approximate where overlap made an exact count ambiguous.
- No robot actions were executed.
