# Parsed State

Source image: `00_capture.jpg`

## Visual Summary

- The table is still active and the robot remains visible on the right.
- The human opponent's hand is moving near the table, so the scene should be
  treated as unstable for automation.
- The robot hole cards are not clearly readable in this image.
- The visible "Your Turn" marker remains near the robot seat, but the human
  motion makes immediate action unsafe.

## State JSON

```json
{
  "loop_stage": "atom_idle",
  "robot": "dexterous hand is near its initial pose and not holding a card or chips",
  "table": {
    "scene_stable": false,
    "uncertain_fields": ["robot", "my_chips", "opponent_chips"],
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {"5": 4, "10": 3, "50": 3, "100": 3},
    "opponent_chips": {"5": 3, "10": 5, "50": 3, "100": 4},
    "my_current_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "opponent_bet": {"5": 0, "10": 0, "50": 0, "100": 0}
  }
}
```
