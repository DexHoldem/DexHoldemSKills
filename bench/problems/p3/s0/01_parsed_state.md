# Parsed State

Source image: `00_capture.jpg`

## Visual Summary

- The physical table is visible and stable.
- The "Your Turn" marker is visible near the robot seat.
- Two robot hole cards are face-down near the bottom seat.
- The big blind marker is at the robot seat.
- The dexterous hand is near its initial pose and is not holding a card or chips.
- No community cards are visible.

## State JSON

```json
{
  "loop_stage": "idle",
  "robot": "dexterous hand is near its initial pose and not holding a card or chips",
  "table": {
    "scene_stable": true,
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {"5": 4, "10": 4, "50": 4, "100": 4},
    "opponent_chips": {"5": 4, "10": 4, "50": 4, "100": 4},
    "my_current_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "opponent_bet": {"5": 0, "10": 0, "50": 0, "100": 0}
  }
}
```
