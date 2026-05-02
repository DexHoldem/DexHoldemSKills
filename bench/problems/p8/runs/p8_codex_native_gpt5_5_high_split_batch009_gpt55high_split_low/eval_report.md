# DexHoldem Perception Report

Current state: `s6`

## Outcome

- Scene stable: no, medium confidence.
- Turn: yes, it is our turn.
- Community cards: none readable; only face-down backs visible.
- Buttons: dealer on opponent side; small blind on opponent side; big blind on robot.
- Bets: robot-side current bet counted as 1 red chip; opponent-side bet unclear.
- Held card: visible but not strictly readable; likely `4d`, treated as uncertain.
- Chip inventory: no completed read returned before timeout.

## Evidence Notes

- The turn detector found a visible `Your Turn` puck near the lower-left player area.
- The board row did not expose readable ranks or suits on the community cards.
- The opponent-side chip cluster overlapped with non-bet chips, so a clean count was not reliable.
- The near robot-held card was partially occluded by the gripper, preventing strict identification.

## Raw Evidence

All requested raw evidence files were written under `visual_raw/`.
