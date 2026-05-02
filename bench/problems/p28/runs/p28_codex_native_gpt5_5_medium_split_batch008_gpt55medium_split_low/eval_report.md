# DexHoldem Perception Report

- Run: `p28_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`
- State: `s24`
- Output directory: `runs/p28_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`

## Results

- Scene stable: `false`
- My turn: `true`
- Dealer: `opponent`
- Small blind: `opponent`
- Big blind: `robot`
- Community cards read: `7d`, `6c`
- Held cards: unreadable

## Chip Inventory

- Robot: red 5 = 6, blue 10 = 3, green 50 = 7 visible, brown 100 = 0 visible
- Opponent: red 5 = 3, blue 10 = 5, green 50 = 4, brown 100 = 2

## Evidence Notes

- Community card evidence came from `community_cards_agent`.
- Turn detection came from `turn_detection_agent`.
- Scene stability came from `scene_stability_agent`.
- Blind buttons came from `blind_button_recognition_agent`.
- Held card recognition reported no readable hole card.
- Chip counts were partially occluded and include uncertainty notes from the subagent.

## Reasoning

- The reasoning subagent was not invoked because no `choose_poker_action` routing was required.
