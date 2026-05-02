# Eval Report

Latest state: `s25`

Merged perception:

- Scene stability: unstable. The robot hand changed between `s24` and `s25`, and the board state also changed.
- Turn ownership: it is our turn. The white turn button is near the lower-left robot seat.
- Board: 3 community cards are visible, read as `7d`, `9s`, `7c` from left to right among the face-up cards.
- Blind assignment: dealer and small blind are on the opponent seat; big blind is robot.
- Bets: both bet areas are partially occluded, so counts are approximate.
- Inventory: both chip stacks are visible with minor occlusion on the lower-right / upper-right groups.
- Held card: no readable robot-held card.
- Showdown: not visible.

Operational conclusion:

- Do not execute a robot action from this frame.
- The capture is not stable enough for a committed next-step decision.
- The next perception pass should wait for a settled frame and then recapture.
