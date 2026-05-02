# DexHoldem Perception Eval Report

Run root: `runs/p1_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low`

## Result

The perception step was run using local setup and subagent evidence only. No robot actions were executed.

## Evidence

- `s0/00_capture.jpg` shows a likely stable table scene.
- The image contains a visible `Your Turn` marker, so the turn state is likely active for the player.
- Five community-card positions are visible, but the card faces are not exposed.
- A `BIG BLIND` marker is visible.
- Chip stacks are visible, but exact values are not reliably readable.

## Notes

- Raw evidence was written to `visual_raw/visual_agent.md`.
- The structured summary was written to `visual_summary.json`.
- No poker action was requested by the router, so the reasoning subagent remained on standby.
