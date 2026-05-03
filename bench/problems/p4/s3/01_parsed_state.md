# Parsed State

Source image: `00_capture.jpg`

## Visual Summary

- Source raw image is `bench/bench_raw/5.jpg`.
- Loop stage: `acting`.
- dexterous hand is lifting the left hole card; the card face is not readable.

## State JSON

```json
{
  "loop_stage": "acting",
  "robot": "dexterous hand is lifting the left hole card; the card face is not readable",
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
