Source: visible subagent `bet_recognition_agent`

```json
{
  "my_current_bet": {
    "counts": {
      "red_5": 2,
      "blue_10": 3,
      "green_50": 0,
      "brown_100": 2
    },
    "evidence": "Left betting area beside the community cards shows one isolated red chip plus a central cluster with three blue, one red, and two brown chips.",
    "uncertain": [
      "One or more chips in the left cluster are partially overlapping; brown-vs-dark-edge visibility is slightly obscured."
    ]
  },
  "opponent_bet": {
    "counts": {
      "red_5": 2,
      "blue_10": 1,
      "green_50": 2,
      "brown_100": 2
    },
    "evidence": "Right betting area beside the community cards shows a compact cluster of seven chips: two red, one blue, two green, and two brown.",
    "uncertain": [
      "The right-side stack is partially overlapped, so exact denomination assignment has minor uncertainty."
    ]
  }
}
```
