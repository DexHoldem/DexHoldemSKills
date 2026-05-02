# Perception Run Report

## Outcome

Current step `s30` was parsed from the latest capture without executing any robot action.

## Consolidated Perception

```json
{
  "state": "s30",
  "scene_stable": false,
  "is_my_turn": true,
  "dealer": "opponent",
  "small_blind": "opponent",
  "big_blind": "robot",
  "community_cards": ["Qh?", "4d?"],
  "my_chips": {
    "red_5": 6,
    "blue_10": 3,
    "green_50": 0,
    "brown_100": 0
  },
  "opponent_chips": {
    "red_5": 1,
    "blue_10": 2,
    "green_50": 1,
    "brown_100": 0
  },
  "my_current_bet": {
    "red": 0,
    "blue": 0,
    "green": 0,
    "brown": 0
  },
  "opponent_bet": {
    "red": 0,
    "blue": 1,
    "green": 0,
    "brown": 0
  }
}
```

## Evidence Notes

- `scene_stable` was judged false because the robot hand is still over the table and appears to be handling a chip.
- `is_my_turn` was judged true from the visible `Your Turn` button.
- Blind assignment was inferred from the visible `BIG BLIND` button on the robot side in heads-up play.
- The board appears to show two partially occluded community cards, read only with uncertainty.
- Chip counts and bet counts were taken from the visible inventories and betting area only; occluded chips were not counted.

## Raw Evidence

- `visual_raw/00_capture.jpg`
