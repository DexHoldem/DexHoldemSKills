# DexHoldem Perception Report

- Run: `p16_codex_native_gpt5_5_medium_split_batch008_g55medium_split_low`
- Latest state: `s15`
- Capture: `s15/00_capture.jpg`

## Evidence Summary

- Community cards: none visible on the board.
- Turn state: it is our turn.
- Scene stability: not stable enough to continue.
- Robot behavior: robot hand is still in motion holding a `5d` hole card.
- Blind buttons: dealer is opponent, big blind is robot, small blind inferred as opponent.
- Held card: readable as `5d`.
- Bets: robot/player bet appears to be `green x2`, `blue x1`, `brown x1`; opponent bet appears to be `green x2`, `blue x2`.
- Chip inventory: both stacks were counted with medium confidence where occluded.

## Assessment

The perception step is complete, but the scene should be treated as unstable because the robot is still actively manipulating the card. No robot action was executed by this run.

## Notes

- Raw evidence files were written under `visual_raw/`.
- The summary reflects only subagent evidence merged by the main agent.
