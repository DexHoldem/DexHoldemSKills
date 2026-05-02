# Perception Step Report

- Scene stability: unstable.
- Turn detection: it is our turn.
- Community cards: `Ts`, `8h`, `7d`, `6s`, `7c`.
- Held card: unreadable; no visible hole card in the gripper.
- Blinds/buttons: dealer and small blind on opponent; big blind on robot.
- Bet areas: partial counts observed in both bet zones, with occlusion.
- Chip inventory: robot about `4/5/2/4` for `5/10/50/100`; opponent about `2/4/3/2`, with some mixed-cluster uncertainty.
- Robot behavior: hand extended from the right, gripper empty, frame still in progress.

The visual evidence conflicts with the cached parsed state for the board cards, so I kept the merged output strictly to the subagent results. No robot actions were executed.
