# DexHoldem Perception Report

- Run id: `p57_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low`
- Capture: `s0/00_capture.jpg`
- Result: stable table state, but it is not the robot's turn.

## Perception Summary

- Scene stability: stable enough to continue.
- Turn detection: not the robot's turn.
- Dealer / blinds: dealer is robot; robot is small blind; opponent is big blind.
- Community cards: `Kh 3s 3c 7h Tc`
- Robot current bet: `10x1, 50x1, 100x1`
- Opponent current bet: `50x4`
- Robot inventory: `5x5, 10x5, 50x2, 100x2`
- Opponent inventory: `5x6, 10x7, 50x1, 100x2`
- Robot-held hole card: not visibly held.

## Routing Note

No poker-action reasoning was needed because the turn detector reported that it is not the robot's turn. No robot actions were executed.
