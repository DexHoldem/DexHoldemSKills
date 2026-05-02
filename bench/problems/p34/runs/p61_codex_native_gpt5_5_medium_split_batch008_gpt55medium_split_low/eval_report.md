# DexHoldem Perception Step

Frame: `s0/00_capture.jpg`

Merged visual evidence:
- Turn detection: it is not our turn.
- Community cards: `4c As Jd` are visible.
- Bet recognition: robot/player current bet totals 30; opponent current bet totals 270.
- Blind buttons: dealer and small blind are on the opponent side; big blind is on the robot side.
- Scene stability: unstable.
- Robot behavior: robot hand is extended mid-action; no immediate collision or safety issue visible.

Assessment:
- The run has valid raw evidence files under `visual_raw/`.
- No robot action was executed.
- The scene is not ready for an action commit because the turn button is not on the robot side and the scene is still reported as unstable.
