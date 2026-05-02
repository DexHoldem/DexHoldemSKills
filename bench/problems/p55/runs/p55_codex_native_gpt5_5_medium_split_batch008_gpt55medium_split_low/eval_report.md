# DexHoldem Perception Step

Status: complete.

## Visual Evidence

- `scene_stability_agent`: stable; robot hand settled on the right side, no visible object motion.
- `turn_detection_agent`: not our turn; white turn button is on the opponent/top side.
- `community_cards_agent`: four community cards are visible, `3s 3c 5d Tc`.
- `held_card_recognition_agent`: no readable held card is visible.
- `blind_button_recognition_agent`: dealer/small blind is at the robot seat; big blind is the opponent.
- `bet_recognition_agent`: my current bet shows `2x 5` and `1x 100`; opponent bet shows `2x 10` and `2x 50`.
- `chip_recognition_agent`: robot inventory `3x 5, 2x 10, 1x 50, 1x 100`; opponent inventory `3x 5, 4x 10, 2x 50, 3x 100`.
- `robot_behavior_agent`: hand is idle/settled, not holding cards or chips.

## Parsed State

- Scene stable: yes
- Our turn: no
- Board: turn, with four visible community cards
- Blinds: dealer/small blind robot, big blind opponent
- Held card visible: no

## Notes

- The main agent did not inspect the image directly.
- No robot action was executed.
- Raw evidence files were written under `visual_raw/`.
