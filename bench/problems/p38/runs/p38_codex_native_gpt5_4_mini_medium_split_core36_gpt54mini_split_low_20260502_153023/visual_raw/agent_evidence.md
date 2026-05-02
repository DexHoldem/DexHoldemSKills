# Visual Evidence

## Scene Stability
- Compared `s34/00_capture.jpg` vs `s33/00_capture.jpg`
- Evidence: robot hand/camera assembly shifted right and lower-right; occlusion and card layout changed between frames
- Conclusion: unstable

## Robot Behavior
- Comparison was not available to the agent in one response; workflow context was `loop_stage=atom_idle`, `current_step=continue_cached_action_sequence`, `pending`
- Hand pose / held object / near-rest / safety / retryability: not directly resolved from that response

## Turn Marker
- `Your Turn` button visible
- Conclusion: it is our turn

## Blind Button
- Yellow `BIG BLIND` button visible on robot-side/lower area
- Conclusion: robot is big blind

## Community Cards
- Left to right: `Ts`, `8h`, `7d`, `8s?`, unreadable/occluded

## Held Card
- Robot hand is visibly holding `9d`

## Chip Inventory
- Robot/player: 5=4, 10=3, 50=3, 100=2
- Opponent: 5=2, 10=4, 50=3, 100=2

## Current Bets
- Robot/lower: 5=4, 10=3, 50=3, 100=2
- Opponent/upper: 5=2, 10=5, 50=2, 100=2

## Showdown
- Opponent hole cards face-up
- Robot hole cards: `9d` and cached `5d`
- Board partially occluded; exact final hand/outcome not fully locked
