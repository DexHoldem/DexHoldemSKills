# Visual Evaluation Report

Run: `p3_codex_split_gpt54mini_fasttest_001`  
Latest state: `s1`  
Source image: `s1/00_capture.jpg`  
Visual setting: `split`

## Merged Judgment

The current frame is visually stable enough to continue, and it is our turn. The robot hand remains extended over the lower-center/right table area and is not at rest, but the frame itself looks settled and shows no obvious physical failure. No showdown is visible.

Final label: `stable_our_turn_no_showdown`

## Agent Evidence

- `scene_stability_agent`: Stable enough to continue. No visible motion blur or active repositioning is present.
- `robot_behavior_agent`: Robot hand is extended from the right, hovering over the lower-center/right betting/community area. It does not appear to be holding a card or chips, and no obvious failure is visible.
- `turn_detection_agent`: It is our turn. The white button near the lower-left area reads `Your Turn`.
- `blind_button_recognition_agent`: Dealer is opponent, small blind is opponent, and big blind is robot.
- `community_cards_agent`: Three community-card positions are visible, but all are unreadable face-down backs.
- `held_card_recognition_agent`: The robot-held card area is occluded; no rank or suit is readable.
- `bet_recognition_agent`: Robot current bet area shows 4 red and 4 blue chips. Opponent current bet area shows 3 red and 4 blue chips. Edge occlusion affects both lanes.
- `chip_recognition_agent`: Only red/blue inventory chips are clearly countable. Both sides show 4 red and 4 blue; green and brown are not clearly visible.
- `showdown_outcome_agent`: No showdown is visible. No readable hole cards, no readable board, and no clear fold or pickup evidence are present.

## Conservative State Summary

- Scene stable: `true`
- Loop stage: `acting`
- Turn marker: our turn
- Blinds: dealer/opponent, small blind/opponent, big blind/robot
- Community cards: none readable
- Robot held card: none visible/readable
- Winning-condition judgment: `not_applicable_or_unclear`

The summary is limited to the evidence returned by the scoped visual agents.
