# DexHoldem Perception Step

Run ID: `p2_codex_split_batch007_codexbase_split_low`

## Summary
The current capture supports a stable-scene assessment, but it does not support a poker-action decision. The board shows five face-down community cards, no readable robot hole card, and no decidable showdown outcome. A yellow `BIG BLIND` marker is visible, but dealer and small-blind assignment remain uncertain.

## Evidence Used
- `scene_stability_agent`: stable, medium confidence.
- `turn_detection_agent`: turn button not safely identifiable, low confidence.
- `community_cards_agent`: five community cards visible, all face-down and unreadable.
- `held_card_recognition_agent`: no readable hole card visible.
- `blind_button_recognition_agent`: partial / uncertain; `BIG BLIND` marker visible.
- `bet_recognition_agent`: partial counts for both betting areas, approximate.
- `chip_recognition_agent`: partial inventory counts in both seat bands, approximate.
- `robot_behavior_agent`: robot hand extended and hovering/reaching, not grasping anything.
- `showdown_outcome_agent`: not showdown / outcome not decidable.

## Merged Assessment
- `scene_stable`: `true`
- `showdown`: `false`
- `community_cards_visible`: `5`
- `hole_cards_readable`: `false`
- `turn_button_identifiable`: `false`

## Notes
- Main-agent image perception was not performed.
- No robot actions were executed.
- The reasoning subagent was not required because the router did not reach `choose_poker_action`.
