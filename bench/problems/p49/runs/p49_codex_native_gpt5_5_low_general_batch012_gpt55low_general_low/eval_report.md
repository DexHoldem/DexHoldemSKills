# DexHoldem Perception Step

State: `s48`

## Outcome
- `scene_stable`: false
- `is_my_turn`: true
- `community_cards`: `Qs`, `Qh`, `7d`, `Qc`, `7c`
- `my_hole_cards`: `Qd`, `5d`
- `blind_button_orientation`: robot side is big blind; opponent side is dealer and small blind

## Evidence
- Visual subagent evidence indicates the robot hand changed position substantially between `s47` and `s48`, so the scene is not settled.
- A white `Your Turn` marker is visible at the lower-left seat area.
- The yellow `BIG BLIND` marker is on the lower robot side.
- Board cards and hole cards were read from the visual subagent output; chip totals were not treated as reliable because of occlusion and overlap.

## Notes
- The reasoning subagent could not complete because the visible agent setup does not support the `inherit` model in this account/runtime combination.
- No robot actions were executed.
