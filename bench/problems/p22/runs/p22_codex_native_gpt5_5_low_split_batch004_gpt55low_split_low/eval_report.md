# Eval Report

State `s20` is not visually settled enough to advance as a stable perception checkpoint.

- Scene stability: unstable, because the robot arm moved substantially between `s19` and `s20` and is still over the central chip/card area.
- Turn state: it is our turn.
- Community cards: none readable.
- Blind/dealer assignment: dealer and small blind are on the opponent side; big blind is the robot.
- Bets: opponent bet is the clearer stack at about 65; robot/player bet is partially occluded and estimated at about 20.
- Inventory: visible chip inventory was read, but both sides have occlusion uncertainty.
- Held card: unreadable.
- Showdown: not visually decided.

No robot actions were executed. No Texas Hold'em reasoning subagent was invoked because the router did not request `choose_poker_action`.
