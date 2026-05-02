# DexHoldem Perception Report

State: `s36`

The current capture is not fully stable. The robot hand is still active over the table, and the arm occludes part of the betting/card area.

Merged visual evidence:

- Dealer / blind assignment: `robot` appears to have the dealer button and the small blind; `opponent` has the big blind.
- Turn button: unclear from the merged evidence because the physical turn/dealer indicators are partially ambiguous.
- Community cards: 2 visible, likely `9s` and `5c`, both uncertain.
- Held card: no readable robot-held hole card visible.
- Bet state: opponent current bet is reported as `red=2, blue=5`; player current bet is reported as `red=4, blue=4, brown=1?`.
- Chip inventory: player roughly `red=4, blue=4`; opponent roughly `red=2, blue=4`, with minor occlusion uncertainty on both sides.
- Showdown: not decidable from this frame alone.

Conclusion:

- Do not execute any robot action from this perception pass.
- The safest interpretation is that the scene is still in progress and needs a stable follow-up frame before any action-dependent decision.
