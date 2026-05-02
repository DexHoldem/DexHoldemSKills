# DexHoldem Perception Step

Status: incomplete for action execution because the scene is unstable.

## Visual Evidence

- [scene_stability_agent.md](./visual_raw/scene_stability_agent.md)
- [turn_detection_agent.md](./visual_raw/turn_detection_agent.md)
- [community_cards_agent.md](./visual_raw/community_cards_agent.md)
- [held_card_recognition_agent.md](./visual_raw/held_card_recognition_agent.md)
- [bet_recognition_agent.md](./visual_raw/bet_recognition_agent.md)
- [chip_recognition_agent.md](./visual_raw/chip_recognition_agent.md)
- [robot_behavior_agent.md](./visual_raw/robot_behavior_agent.md)
- [reasoning_agent.md](./visual_raw/reasoning_agent.md)

## Summary

- Scene stability: unstable.
- Turn: it is our turn.
- Community cards: 5 positions reported, with the first two unreadable/face-down and the last three read as `3c`, `Ah`, and `Tc` with uncertainty.
- Held card: no readable held card visible.
- Bets: robot/player current bet is red x2; opponent bet is zero across all denominations.
- Robot behavior: hand is extended from the right and not settled.

## Reasoning Recommendation

- Conservative poker recommendation was to avoid adding chips or raising.
- If a poker action must be chosen, the reasoning subagent recommended `check` if legal, otherwise `fold` if any amount must be called.

## Notes

- No robot action was executed.
- The main risk is visual instability, especially due to active human hands near the betting area and the robot hand still in motion.
