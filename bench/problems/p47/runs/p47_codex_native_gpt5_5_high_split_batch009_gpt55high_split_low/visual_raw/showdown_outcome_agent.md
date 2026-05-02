Source agent: showdown_outcome_agent

Returned evidence:
Showdown state: yes, likely showdown. Five community cards are exposed and both players’ hole cards appear face-up.

Visible reads:
- Community board: appears to be Qx Qx 7d 6s 7c-type board, with paired queens and paired sevens.
- Robot hole cards: face-up, appears Qd 5d; no cache needed.
- Opponent hole cards: face-up; right card appears to be Qc, left black spade card is not fully readable.

Outcome evidence:
- If the board/opponent reads are correct, both robot and opponent appear to hold a queen.
- With paired queens and paired sevens on board, both would make queens full of sevens using their queen.
- That points to a likely tie, not a clear robot win or loss.

Recommended loop-stage label: showdown / showdown-visible.

Do not decide win/lose from this frame: exact opponent left card is unclear, and the visible comparison suggests possible tie rather than a clear winner.
