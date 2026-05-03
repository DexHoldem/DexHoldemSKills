# Parsed State

Source image: `00_capture.jpg`

## Visual Summary

- Source raw image is `bench/bench_raw/15.jpg`.
- Loop stage: `acting`.
- dexterous hand is moving through the right hole-card pickup sequence.

## State JSON

```json
{
  "loop_stage": "acting",
  "robot": "dexterous hand is moving through the right hole-card pickup sequence",
  "table": {
    "scene_stable": false,
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {
      "5": 4,
      "10": 4,
      "50": 4,
      "100": 4
    },
    "opponent_chips": {
      "5": 3,
      "10": 4,
      "50": 4,
      "100": 4
    },
    "my_current_bet": {
      "5": 0,
      "10": 0,
      "50": 0,
      "100": 0
    },
    "opponent_bet": {
      "5": 1,
      "10": 0,
      "50": 0,
      "100": 0
    }
  }
}
```
