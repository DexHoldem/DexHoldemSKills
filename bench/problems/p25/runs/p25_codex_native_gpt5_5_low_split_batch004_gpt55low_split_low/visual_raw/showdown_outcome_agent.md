Not showdown.

Evidence:
- Community cards are still face-down; no board is revealed.
- Opponent hole cards are not face-up or readable.
- Robot hole cards appear face-down, so robot values would need to come from cache if needed.
- No exposed opponent cards, mucked/revealed hands, pushed pot, or chip collection action clearly indicates win/loss.
- Dealer/button markers and chips are visible, but they do not establish showdown outcome.

Recommended loop-stage label: not_showdown / in_hand_unclear_state.

Uncertainty:
- Cannot decide win, loss, or tie from this frame.
- No best-hand comparison is possible because the board and opponent hole cards are unreadable/unrevealed.
