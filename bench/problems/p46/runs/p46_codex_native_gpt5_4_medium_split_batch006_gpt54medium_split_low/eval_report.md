# Eval Report

Current perception step: `s45`

Merged result:

- Scene is not stable enough to treat as settled.
- It is our turn.
- Dealer button is on the opponent seat.
- Opponent is small blind; robot is big blind.
- Community cards read `Ts 8h 7d 6s 7c`.
- Held hole cards are not readable from this frame.
- My current bet and opponent bet were merged from the bet-recognition agent, with medium confidence and noted occlusion risk.
- Chip inventory is `robot: 4/3/3/4` and `opponent: 2/4/3/3` by `5/10/50/100`.
- Robot behavior indicates the hand is still mid-action over the upper-right table area.

Action taken:

- No robot action executed.

Notes:

- This pass used only scoped visual subagents and merged their evidence.
- The reasoning subagent was not needed because no poker-action decision was requested by the router for this run.
