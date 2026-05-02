# DexHoldem Perception Step

## Result

- Scene is stable.
- It is not our turn.
- No robot action was executed.

## Visual Evidence

- The turn button is on the opponent/top side of the table, not the robot/player side.
- Five community-card positions are visible, but they appear face down.
- Visible chips in the lower player zones look like inventory chips rather than forward bets.
- The right side of the table is heavily occluded by the robot arm and camera assembly.

## Subagent Notes

- Visual subagent 1 confirmed the scene is stable and not our turn.
- Visual subagent 2 confirmed the board/chip zoning and noted the occlusion.
- The requested reasoning subagent could not be used as configured because its `inherit` model is unsupported in this environment.

## Files Written

- `visual_raw/visual_agent_stability_turn.txt`
- `visual_raw/visual_agent_cards_chips.txt`
- `visual_summary.json`
- `eval_report.md`
