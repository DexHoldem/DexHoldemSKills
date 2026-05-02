# Eval Report

The current perception step indicates the scene is still unstable, so no robot action was executed.

## Merged Evidence
- Scene stability: unstable; the robot arm/camera assembly and hand are still shifting between `s0/00_capture.jpg` and `s1/00_capture.jpg`.
- Turn detection: it is our turn; the white "Your Turn" button is visible near the lower-left seat.
- Community cards: none visible.
- Held card visibility: a robot-held card is visible but unreadable.
- Blind/button assignment: the big blind is clearly marked at seat 5; dealer/small blind appear to be at seat 6 with some uncertainty.
- Bets/chips: both chip recognition and bet recognition returned approximate counts with partial occlusion.

## Decision
- Do not act yet.
- The correct next router outcome is `wait` and recapture after the scene settles.
