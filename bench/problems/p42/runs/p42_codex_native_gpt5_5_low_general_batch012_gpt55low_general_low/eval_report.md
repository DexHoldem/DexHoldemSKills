# DexHoldem Perception Report

Run: `p42_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low`
State: `s38`

## Result

Perception-only step completed. No robot actions were executed.

## Merged Evidence

- The table view is stable enough for inspection.
- The right-center area is partially occluded by the robot gripper/camera assembly.
- Community cards appear to include `Q♠`, `8♥`, `7♦`, and `9♣`.
- A rightmost card is present but not reliable enough to name with confidence.
- Hero-side visible card evidence includes `Q♦`.
- The robot gripper is visibly holding `5♦`.
- Opponent-side visible card evidence suggests `A♠` and `10♣`, but confidence is lower than for the board.
- `Your Turn`, `DEALER`, and `BIG BLIND` markers are visible.
- Multiple chip stacks are visible, with denominations including `5`, `10`, `50`, and `100`.

## Reasoning Check

The reasoning subagent confirmed that no Texas Hold'em action reasoning is required for this perception-only step.

## Notes

- Exact chip counts are not reliable from this frame.
- The rightmost community-card area is partially blocked and should be treated as uncertain.
- Raw evidence is stored under `visual_raw/`.
