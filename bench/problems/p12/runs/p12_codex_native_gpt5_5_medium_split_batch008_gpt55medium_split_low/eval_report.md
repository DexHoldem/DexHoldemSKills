# DexHoldem Perception Report

Run: `p12_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`

Latest state: `s7`

## Summary

- Community cards: no readable face-up board cards.
- Blind buttons: dealer and small blind are on the opponent; big blind is on the robot.
- Turn: it is our turn.
- Held card: no readable robot-held card visible.
- Scene stability: unstable due to robot occlusion over the right side of the table.
- Robot behavior: robot hand is active or recently active over the play area.
- Inventory chips: counts were estimated by the chip subagent with some occlusion uncertainty.
- Showdown: not at showdown.

## Notes

- The main agent did not perform image perception.
- Evidence came only from scoped visual subagents.
- Raw evidence files were written under `visual_raw/`.
