# Eval Report

## Outcome

Perception step completed from visible subagent evidence only. No robot actions were executed.

## Parsed State

- `scene_stable`: `false`
- `is_my_turn`: `true`
- Community cards visible: `Qs`, `Qh`, `7d` with occlusion uncertainty, `Qc`, and one unreadable/occluded card
- Robot-held hole card: unreadable
- Dealer: opponent
- Small blind: opponent
- Big blind: robot

## Chip Evidence

- Robot inventory chips: approximately 5 red 5-chips and 4 blue 10-chips visible; green and brown inventory chips were not countable
- Opponent inventory chips: approximately 3 red 5-chips and 6 blue 10-chips visible; green and brown inventory chips were not countable
- Current bet chips: robot side none visible; opponent side approximately 2 red 5-chips and 5 blue 10-chips

## Reliability Notes

- The scene was judged unstable because the robot arm is still extended over the table and partially occludes the state.
- The turn button was visible and safely identifiable.
- Community card position 3 and position 5 remain uncertain.

## Files Written

- `visual_raw/community_cards_agent.md`
- `visual_raw/held_card_recognition_agent.md`
- `visual_raw/turn_detection_agent.md`
- `visual_raw/blind_button_recognition_agent.md`
- `visual_raw/chip_recognition_agent.md`
- `visual_raw/bet_recognition_agent.md`
- `visual_raw/scene_stability_agent.md`
- `visual_summary.json`
