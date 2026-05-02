# Eval Report

Current perception result for `s37`:

- `scene_stable`: false
- `is_my_turn`: false
- `community_cards`: `Ts`, `8h`, `7d`, `6s`, `7c`
- `dealer`: opponent
- `small_blind`: opponent
- `big_blind`: robot

Additional evidence:

- Robot hole card visibility is unresolved because the hand is occluding the card area.
- Robot behavior subagent reports the gripper is still extended over the active play area.
- Current bets and chip inventories were read from the table, but no action was taken because it is not the robot's turn.
- Showdown subagent indicates this is a `show_hand` frame, but the winner cannot be determined from the visible cards.

Decision:

- Do not execute any robot action.
- Treat the scene as not yet safe for progression based on the hand still in the active area and the non-robot turn state.
