# Perception Step Report

## Result
The current DexHoldem perception step is complete for state `s37`.

## Evidence Summary
- The table is in a later street with five community cards visible: `10s, 8h, 7d, 6s, 7c`.
- The `Your Turn` marker is visible, so it is the robot's turn.
- One hero hole card is visible as `Qd`; the second hole card is occluded by the robot arm.
- A yellow `BIG BLIND` marker is visible near seat 5.
- Chip stacks and bet totals are present, but exact counts are low-confidence because of occlusion and perspective.

## Stability
- The scene is mostly stationary, but the robot arm occludes part of the near-right hero area.
- Visual extraction is reliable enough for board state and turn detection, but not for exact chip accounting.

## Raw Evidence
- `visual_raw/evidence.txt`

## Notes
- No robot action was executed.
- No main-thread image perception was used; this report merges subagent evidence only.
