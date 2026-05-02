Stable single-frame evidence from `s0/00_capture.jpg`.

Observed state:
- No visible motion in the frame.
- The scene is a completed showdown / lost-hand cleanup state, not a live betting turn.
- Local metadata labels the loop stage as `lose` with intent `handle_lost_hand`.

Evidence details:
- Community cards visible on board: `Kh`, `3s`, `3c`, `5h`, `Tc`.
- Robot hole cards from cache: `Jc`, `6h`.
- Opponent hole cards from cache: `Qs`, `Jd`.
- Chips/bets are already laid out in both bet areas; the robot side has a larger chip cluster than the opponent side.
- The turn state is not actionable; local metadata says opponent's turn, and this is post-showdown cleanup.

Conclusion:
- The robot lost the hand.
- No poker action reasoning is required.
