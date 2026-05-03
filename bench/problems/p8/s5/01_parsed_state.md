# Parsed State

Source image: `00_capture.jpg`

## Visual Summary

- Source raw image is `bench/bench_raw/7.jpg`.
- Loop stage: `atom_idle`.
- dexterous hand is holding the left hole card face-visible to the camera.
- Readable held card: `9d` from the left slot.

## State JSON

```json
{
  "loop_stage": "atom_idle",
  "robot": "dexterous hand is holding the left hole card face-visible to the camera",
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
  },
  "held_card": {
    "position": "left",
    "card": "9d"
  }
}
```
