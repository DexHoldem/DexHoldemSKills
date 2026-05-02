Opponent hole cards are face-up. The readable top/opponent cards appear to be `4s` and `Qc`, though the left card is slightly small.

Robot hole cards are face-up and readable as `Qd` and `5d`.

The community board appears to be `Qs 8h 7d 6s 7c`. With that board, robot has two pair: queens and sevens, with 8 kicker. Opponent with `Qc 4s` also has two pair: queens and sevens, with 8 kicker from the board. This looks like a tie if all card reads are correct.

Recommended loop-stage label: `show_hand`, not `win` or `lose`, because the result appears tied and the opponent left card/board reads should be confirmed before deciding.
