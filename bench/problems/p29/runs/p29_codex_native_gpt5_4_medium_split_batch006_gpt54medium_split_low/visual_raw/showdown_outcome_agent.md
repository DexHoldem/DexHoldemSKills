# showdown_outcome_agent

Showdown evidence is not visible.

Visible evidence:
- No player hole cards are face-up.
- Opponent hole cards are not readable; the visible cards near the top seats appear face-down.
- Robot hole cards are also face-down in the bottom-right seat, so there is no visible robot hand read from the image.
- Three community cards are face-up on the board, but at least two board positions are still face-down / unresolved in the image.

Assessment:
- `showdown_visible`: no
- `opponent_cards_face_up`: no
- `robot_cards_face_up`: no
- `win_or_loss_clear`: no
- `recommended_loop_stage`: `in_hand_not_showdown` (best-fit label)

Reason not to decide:
- No revealed hole cards for either side
- Board is not fully resolved / visibly complete
- No pot-award or chip-collection evidence tied to a winner
- No fold action is clearly shown in this frame
