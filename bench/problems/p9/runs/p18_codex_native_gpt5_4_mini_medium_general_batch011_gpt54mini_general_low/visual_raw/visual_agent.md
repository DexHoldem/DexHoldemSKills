Visual evidence from read-only subagents

1. Stability read on `s18/00_capture.jpg` vs `s17/00_capture.jpg`
- Result: Unstable.
- Evidence: the right-side robot gripper is holding a visible playing card in `s18`, while that card is not visible in `s17` and the hand pose differs.
- Interpretation: the scene changed between frames, so the latest capture is not settled.

2. Table read on `s18/00_capture.jpg`
- Turn: Yes. A white circular `Your Turn` button is visible in the lower-left robot-seat area.
- Community cards: no face-up community cards are visible; the center board shows face-down card backs only.
- Chips / bets:
  - Lower-left robot-seat zone: small red/cream chip cluster near the inner edge, exact count unclear.
  - Lower-middle seat zone: several blue chips near the `BIG BLIND` button, with inventory versus bet split unclear.
  - Upper-center / dealer zone: mixed chips visible, ownership and counts unclear.
  - Upper-right seat zone: mixed-color chips visible near the inner edge, ownership and counts unclear.
- Robot hand / occlusion: a robotic gripper is visible at bottom-right, occluding part of the right-front chip area.
- Uncertainty: exact denominations and inventory-vs-bet split remain approximate because of perspective and occlusion.
