# DexHoldem Perception Report

## Result

Current state was parsed as `s23` in `to_recover` mode for the cached action `recover_cached_action`.

## Merged Visual Evidence

- Scene stability: `false` at medium confidence.
- Turn detection: `true` at high confidence.
- Community cards: none readable; board remains face-down.
- Chip inventory:
  - Robot: `5=4`, `10=4`, `50=3`, `100=2`
  - Opponent: `5=4`, `10=5`, `50=3`, `100=3`
- Blind assignment:
  - Dealer: opponent
  - Small blind: opponent
  - Big blind: robot
- Held cards: unknown for both slots.

## Interpretation

The capture shows the robot is still considered to be on turn, but the scene is not fully stable because the robot assembly and a person on the opponent side still occlude part of the table. Since this run was only asked to perform perception, no robot action was issued.

## Produced Artifacts

- `visual_raw/`
- `visual_summary.json`
- `eval_report.md`
