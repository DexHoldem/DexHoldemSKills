# Eval Report

## State
Current state: `s7`
Capture: `s7/00_capture.jpg`

## Merged Visual Evidence
- Scene is stable enough to continue.
- It is our turn.
- Hole card is present but unreadable.
- Five community-card positions are visible, but all are face-down/unreadable.
- Dealer/small blind are on the opponent side; big blind is on the robot side.
- Bets are symmetric: `red=3`, `blue=4`, `green=2`, `brown=0` for both sides.
- Chip inventory appears approximately balanced at `4/4/4/4` for both robot and opponent across red, blue, green, and brown chips.
- Robot hand is hovering over the table with no obvious collision, jam, or recovery issue.
- No showdown win/lose evidence is visible.

## Decision
Perception only. No robot action should be executed from this step based on the available evidence.

## Evidence Sources
- [held_card_recognition_agent.md](./visual_raw/held_card_recognition_agent.md)
- [community_cards_agent.md](./visual_raw/community_cards_agent.md)
- [turn_detection_agent.md](./visual_raw/turn_detection_agent.md)
- [scene_stability_agent.md](./visual_raw/scene_stability_agent.md)
- [blind_button_recognition_agent.md](./visual_raw/blind_button_recognition_agent.md)
- [bet_recognition_agent.md](./visual_raw/bet_recognition_agent.md)
- [chip_recognition_agent.md](./visual_raw/chip_recognition_agent.md)
- [robot_behavior_agent.md](./visual_raw/robot_behavior_agent.md)
- [showdown_outcome_agent.md](./visual_raw/showdown_outcome_agent.md)
