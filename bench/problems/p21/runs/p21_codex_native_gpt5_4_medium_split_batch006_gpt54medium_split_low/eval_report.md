# DexHoldem Perception Report

State: `s18`
Capture: `s18/00_capture.jpg`

## Result

- `scene_stable`: `false`
- `is_my_turn`: `true`
- `community_cards`: `[]`

## Merged Visual Evidence

- Scene stability: unstable because the robot arm is still occluding the robot-side card/bet area.
- Turn detection: it is our turn.
- Community cards: no face-up board cards are visible.
- Buttons: dealer and small blind are on the opponent side; big blind is on the robot side.
- Bets:
  - Opponent current bet: `3x blue_10`, `1x green_50`
  - Robot current bet: `1x red_5`
- Held cards:
  - Left card: `5d`
  - Right card: hidden / unreadable

## Output Notes

- No robot actions were executed.
- The action reasoning subagent was requested but failed to initialize in this environment because the `inherit` model is unsupported here.
- Perception outputs were merged from the visual subagents only.
