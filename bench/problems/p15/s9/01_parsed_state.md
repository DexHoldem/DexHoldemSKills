# Parsed State

Source image: `00_capture.jpg`

## Visual Summary

- Source raw image is `bench/bench_raw/14.jpg`.
- Loop stage: `idle`.
- dexterous hand has returned near the table after putting down the left hole card and is ready to view the right hole card.

## State JSON

```json
{
  "loop_stage": "idle",
  "robot": "dexterous hand has returned near the table after putting down the left hole card and is ready to view the right hole card",
  "table": {
    "scene_stable": true,
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {
      "5": 4,
      "10": 4,
      "50": 4,
      "100": 4
    },
    "opponent_chips": {
      "5": 4,
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
      "5": 0,
      "10": 0,
      "50": 0,
      "100": 0
    }
  }
}
```
