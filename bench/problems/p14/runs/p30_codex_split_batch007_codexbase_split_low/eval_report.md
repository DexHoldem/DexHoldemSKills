# Perception Step Report

Current state: `s28`

## Outcome

The scene is **not stable**. The robot arm/end effector is still moving over the table, so the safe perception-only action is to wait for another capture.

## Evidence

- `scene_stability_agent`: unstable; the robot arm moved into the center of the table and changed the visible play area.
- `turn_detection_agent`: it is our turn; the white turn button is visible near the lower-left edge of the table.
- `community_cards_agent`: 4 shared cards are readable as `8h`, `7d`, `6s`, `7c`, with the leftmost community position unreadable/face down.
- `blind_button_recognition_agent`: big blind assigned to opponent; dealer and small blind remain unclear.
- `bet_recognition_agent`: opponent betting area shows `2 red` and `4 blue`; player betting area shows `3 blue` and possibly `1 green`, but the green chip is uncertain.
- `chip_recognition_agent`: inventory counts are approximate due to occlusion.
- `robot_behavior_agent`: robot hand is extended over the right side of the table and still moving.
- `held_card_recognition_agent`: no robot-held hole card is clearly visible.

## Action

No robot action is executed. The perception result supports `wait` until the next stable frame.
