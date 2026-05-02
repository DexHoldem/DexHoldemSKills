## showdown_outcome_agent

Showdown is visible.

- Opponent hole cards are face-up, but only one card is clearly readable as `J`; the other card is not crisp enough to confirm and only looks like a `7`.
- Robot hole cards are face-up as `2♠` and `K♣`.
- The board is face-up and appears to be `K♥ K♠ 4♣ A♠ J♥`.
- Visible best hand for the robot is trips kings (`K♣` plus the two kings on board).

I can’t safely call `win` or `lose` from this image alone because the opponent’s second hole card is not fully readable. Recommended stage: `show_hand`.
