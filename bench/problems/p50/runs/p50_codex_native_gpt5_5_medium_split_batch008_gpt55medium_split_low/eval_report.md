# DexHoldem Perception Report

- Run: `p50_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`
- Capture: `s50/00_capture.jpg`
- Scene stability: false
- Turn state: robot/player turn
- Board: complete with `Qs`, `Qh`, `7d`, `6s`, `Jc`
- Blinds/button state: dealer opponent, small blind opponent, big blind robot

## Bet Evidence

- My current bet: `red=3, blue=0, green=0, brown=0`
- Opponent bet: `red=0, blue=0, green=2, brown=3`

## Interpretation

The perception step indicates the robot has the turn, but the scene is not stable enough to advance with an automatic action judgment. The gripper is still extended into the betting area, so the safest router outcome is to treat this as an in-progress physical state and wait for stability before any downstream action reasoning.

## Evidence

- `visual_raw/community_cards.txt`
- `visual_raw/turn_detection.txt`
- `visual_raw/scene_stability.txt`
- `visual_raw/bet_recognition.txt`
- `visual_raw/blind_buttons.txt`
