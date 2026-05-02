# Parsed State

Source image: `00_capture.jpg`

## Visual Summary

- Three community cards are visible on the board.
- The dexterous hand is still visible on the right side and does not appear to
  be holding a card.
- The robot's hole cards remain face-down or unclear from this frame.
- Because the example lacks cached hole-card data, the agent should execute a
  view-card sequence before any betting decision.

## State JSON

```json
{
  "loop_stage": "idle",
  "robot": "dexterous hand is near its initial pose and not holding a card or chips",
  "table": {
    "scene_stable": true,
    "uncertain_fields": ["community_cards", "my_chips", "opponent_chips", "my_current_bet", "opponent_bet"],
    "is_my_turn": true,
    "community_cards": ["unknown", "unknown", "unknown"],
    "my_chips": {"5": 4, "10": 3, "50": 3, "100": 3},
    "opponent_chips": {"5": 3, "10": 5, "50": 3, "100": 4},
    "my_current_bet": {"5": 2, "10": 0, "50": 0, "100": 0},
    "opponent_bet": {"5": 2, "10": 1, "50": 0, "100": 2}
  }
}
```
