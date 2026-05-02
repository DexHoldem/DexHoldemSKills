# Parsed State

Source image: `00_capture.jpg`

## Visual Summary

- The physical table is visible with the robot on the right side of the frame.
- The "Your Turn" marker is visible near the bottom-left robot seat area.
- Two robot hole cards appear face-down near the bottom seat.
- The dexterous hand appears near its initial pose and is not holding a card.
- Community cards are not visible yet.

## State JSON

```json
{
  "loop_stage": "idle",
  "robot": "dexterous hand is near its initial pose and not holding a card or chips",
  "table": {
    "scene_stable": true,
    "uncertain_fields": ["my_chips", "opponent_chips"],
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {"5": 6, "10": 5, "50": 4, "100": 4},
    "opponent_chips": {"5": 6, "10": 6, "50": 4, "100": 5},
    "my_current_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "opponent_bet": {"5": 0, "10": 0, "50": 0, "100": 0}
  }
}
```
