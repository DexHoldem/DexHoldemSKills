# DexHoldem Perception Report

- Run: `p58_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low`
- State: `s0`

## Visual Evidence

- Scene stability: stable, with the caveat that the subagent did not have a prior frame to compare.
- Turn: it is not our turn.
- Blind assignment: dealer/small blind at the robot seat, big blind at the opponent seat.
- Community cards: `Jh`, `Ac`, `Ks`, `4c`, `Kd`.
- Held card: no readable robot-held card.
- Robot behavior: hand is extended over the right-center table area and appears mid-action but not obviously unsafe.
- Chip inventory: robot `red 1, blue 3, green 0, brown 0`; opponent `red 3, blue 4, green 0, brown 0`.

## Outcome

Perception artifacts were written to the requested run directory, and no robot actions were executed.

## Raw Evidence

- `visual_raw/scene_stability_agent.md`
- `visual_raw/turn_detection_agent.md`
- `visual_raw/blind_button_recognition_agent.md`
- `visual_raw/community_cards_agent.md`
- `visual_raw/robot_behavior_agent.md`
- `visual_raw/held_card_recognition_agent.md`
- `visual_raw/chip_recognition_agent.md`
