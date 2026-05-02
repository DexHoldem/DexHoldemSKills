# DexHoldem Perception Report

Current state: `s25`

Merged judgment:
- Scene stability: unstable
- Turn: not our turn
- Showdown: not visible
- Hole-card visibility: no robot-held card readable
- Next safe step: wait and recapture

Evidence summary:
- The robot hand is still extended over the right-side betting area and looks mid-task rather than settled.
- The white turn button is visible near the lower-left seat, so the turn does not belong to the robot.
- Three community cards are visible: `7d`, `6s` with slight uncertainty, and `7c`.
- Blind buttons place the dealer/small blind on the opponent side and the big blind on the robot side.
- No face-up hole cards or winner/loser state is visible, so showdown is not established.

Action note:
- No robot actions were executed.
- No poker-action reasoning was needed because the turn gate is false and the scene is unstable.
