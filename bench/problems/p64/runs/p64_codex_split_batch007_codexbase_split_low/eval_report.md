# DexHoldem Perception Step

Current state: `s1`

## Visual Findings

- Scene stability: unstable. The camera/framing shifted right and the robot/camera rig is still moving in the foreground.
- Turn: it is our turn. The white `Your Turn` button is visible near the lower-left robot seat.
- Blinds: dealer is at the opponent seat, so opponent is small blind and robot is big blind.
- Community cards: `Kh`, `Ks`, `Ac`, `As`, `Qh`.
- Held card: no visible readable card is being held by the robot hand.
- Robot inventory: `2` red, `2` blue, `0` green, `0` brown, with `2` uncertain chips.
- Opponent inventory: `2` red, `3` blue, `2` green, `1` brown, no uncertainty.
- Top betting area: `2` red, `2` blue, `3` green, `2` brown, `1` uncertain light chip.
- Bottom betting area: `2` red, `2` blue, `2` brown, `1` uncertain light chip.

## Routing Note

The table is not stable enough to commit a poker action from this perception step, so the safe result is to wait for a settled frame before any router action.

## Evidence Sources

- [`scene_stability_agent.md`](./visual_raw/scene_stability_agent.md)
- [`turn_detection_agent.md`](./visual_raw/turn_detection_agent.md)
- [`blind_button_recognition_agent.md`](./visual_raw/blind_button_recognition_agent.md)
- [`community_cards_agent.md`](./visual_raw/community_cards_agent.md)
- [`chip_recognition_agent.md`](./visual_raw/chip_recognition_agent.md)
- [`bet_recognition_agent.md`](./visual_raw/bet_recognition_agent.md)
- [`held_card_recognition_agent.md`](./visual_raw/held_card_recognition_agent.md)

