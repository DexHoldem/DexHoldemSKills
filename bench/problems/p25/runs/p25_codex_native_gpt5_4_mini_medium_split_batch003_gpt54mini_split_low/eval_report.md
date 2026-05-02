# Eval Report

## Result

Perception step completed from merged subagent evidence only.

## Key Findings

- `is_my_turn` is true.
- The scene is not stable.
- Five community-card positions are visible, but all are face-down / unreadable.
- No readable held card is visible in the current capture.
- Dealer/small blind is on the opponent side; the robot is the big blind.
- The robot hand is still in progress over the table, with right-side occlusion.
- Current bet areas are visible but partially occluded; counts are uncertain.
- Inventory chips were estimated from the visual chip agent, also with occlusion caveats.

## Poker-Action Validation

- The visible reasoning subagent could not be used successfully because the runtime rejected the `inherit` model for this account.
- No poker action was committed.

## Notes

- Raw evidence is written under `visual_raw/`.
- `visual_summary.json` records the merged evidence and uncertainty.

