# DexHoldem Perception Step

## Result

The current capture was parsed successfully using only subagent evidence.

## Merged Visual State

- Scene stability: stable.
- Turn: it is our turn.
- Community cards: `3c Js Ks Qd Qh`.
- My current bet: 2 red `5` chips, 3 blue `10` chips.
- Opponent current bet: about 2 blue `10` chips and 2 green `50` chips.
- Robot inventory: about 2 red `5` chips, 1 blue `10` chip, 3 green `50` chips, 4 brown `100` chips.
- Opponent inventory: about 4 red `5` chips, 1 blue `10` chip, 3 green `50` chips, 4 brown `100` chips.
- Blinds: dealer/small blind at robot, big blind at opponent.
- Held-card read: no card visibly held by the robot hand; robot hole cards on the table read as `7h` and `3s`.
- Robot behavior: the dexterous hand still looks active or settling over the right side of the table.

## Showdown Notes

The showdown agent reported face-up hole cards on both sides and a possible tie candidate, but the opponent right hole card is ambiguous. I did not convert that into a hard win/loss label.

## Action Safety

No robot action was executed. The output here is perception-only.

## Files Written

- `visual_raw/scene_stability_agent.md`
- `visual_raw/turn_detection_agent.md`
- `visual_raw/community_cards_agent.md`
- `visual_raw/bet_recognition_agent.md`
- `visual_raw/chip_recognition_agent.md`
- `visual_raw/blind_button_recognition_agent.md`
- `visual_raw/held_card_recognition_agent.md`
- `visual_raw/showdown_outcome_agent.md`
- `visual_raw/robot_behavior_agent.md`
- `visual_summary.json`
