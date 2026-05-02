# Eval Report

Current state: `s4`

## Result

Perception step completed with merged visual evidence only.

## Parsed Table

```json
{
  "scene_stable": true,
  "is_my_turn": true,
  "community_cards": [],
  "dealer_button": null,
  "small_blind": null,
  "big_blind": "robot",
  "my_held_card": null,
  "my_held_card_status": "unreadable",
  "my_current_bet": {
    "red_5": 4,
    "blue_10": 3,
    "green_50": 0,
    "brown_100": 0,
    "uncertain": true
  },
  "opponent_bet": {
    "red_5": 3,
    "blue_10": 4,
    "green_50": 2,
    "brown_100": 1,
    "uncertain": true
  },
  "my_chips": null,
  "opponent_chips": null,
  "showdown_state": false,
  "uncertain_fields": [
    "dealer_button",
    "small_blind",
    "my_held_card",
    "my_chips",
    "opponent_chips",
    "my_current_bet",
    "opponent_bet"
  ]
}
```

## Notes

- Community cards are all face-down, so no board ranks/suits are supported.
- The robot is identified as the big blind.
- The robot-held hole card is present but unreadable.
- The chip inventory worker timed out, so `my_chips` and `opponent_chips` remain unresolved.
- No robot action was executed.
