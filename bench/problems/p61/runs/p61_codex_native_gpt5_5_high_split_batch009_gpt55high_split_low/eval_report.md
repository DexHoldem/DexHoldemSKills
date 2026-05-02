# DexHoldem Perception Step

Status: completed

## Merged Evidence
- Scene is stable enough for perception.
- It is not our turn.
- Community cards visible: `4c`, `As`, `Jd`.
- No robot-held hole cards are readable.
- Blind/button assignment: dealer opponent, small blind opponent, big blind robot.
- Current bets read as robot/player `blue x1, brown x1` and opponent `blue x2, green x3, brown x1`.
- Inventory counts were also captured for both seats.
- Robot hand is extended over the felt with an open, empty pose; no unsafe contact was observed.

## Action
- No robot action executed.
- No poker-action reasoning was requested because the turn detector reported that it is not our turn.

## Notes
- Some chip counts remain partially occluded, so bet and inventory counts should be treated as best-effort visual estimates.
- Raw evidence files were written under `visual_raw/` for each scoped subagent.
