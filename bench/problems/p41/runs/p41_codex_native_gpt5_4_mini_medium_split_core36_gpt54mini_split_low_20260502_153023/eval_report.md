# Eval Report

- Current capture is still mid-action: the robot hand is extended and holding a visible card.
- Scene compatibility with the previous frame is not settled, so `scene_stable` is set to `false`.
- The turn marker indicates it is our turn.
- Blind assignment is `big_blind` for the robot and `small_blind` for the opponent.
- Community board cards visible left to right: `Ts`, `Qh`, `7d`, `6s`, `Jc`.
- Chip inventories and current bets were inherited from the prior parsed state because the dedicated chip/bet agents did not return usable output.
- `loop_stage` is set to `acting` because the physical hand is still moving despite the cached `atom_idle` workflow state.

