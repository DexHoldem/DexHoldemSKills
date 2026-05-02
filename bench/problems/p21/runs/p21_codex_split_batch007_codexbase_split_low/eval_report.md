# DexHoldem Perception Step

## Outcome

- Current capture: `s18/00_capture.jpg`
- Previous capture: `s17/00_capture.jpg`
- Turn status: our turn
- Scene stability: unstable

## Evidence

- Turn detection subagent found the white `Your Turn` button near the lower-left side of the table and not meaningfully occluded.
- Scene stability subagent found the right hole-card area still changing between the last two frames, with the `5d` now present near the gripper and the gripper still parked over the card area.

## Merged Judgment

- `scene_stable = false`
- `is_my_turn = true`
- Next perception action: wait and recapture

## Notes

- No robot actions were executed.
- No poker action reasoning was needed because the scene is not stable enough to advance the router decision.
