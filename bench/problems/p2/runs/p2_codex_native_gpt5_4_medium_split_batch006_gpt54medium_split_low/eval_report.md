# DexHoldem Perception Step

State: `s0`

Summary:
- Scene is unstable; the robot hand is still extended over the upper-right table area.
- It is not our turn.
- No face-up community cards are visible; the board shows five card backs.
- No readable held card is visible.
- No current bets are visible in either betting lane.
- Inventory counts:
  - Robot: 4 red, 4 blue, 4 green, 5 brown.
  - Opponent: 4 red, 5 blue, 4 green, 5 brown.
- Button assignment:
  - Dealer: opponent.
  - Small blind: opponent.
  - Big blind: robot.

Notes:
- No poker-action reasoning was needed because the router did not require a `choose_poker_action` step here.
- No robot actions were executed.
