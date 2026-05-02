# Perception Report

- Latest state: `s37`
- Scene stability: unstable
- Turn detection: it is our turn

## Visual Evidence

- Community cards seen on the current frame: `Ts`, `8h`, `7d`, `9s`, `7c`
- Current bet areas: my bet area shows 2 blue 10-chips, 1 green 50-chip, 2 brown 100-chips; opponent bet area shows 3 red 5-chips, 1 blue 10-chip, 1 green 50-chip, 3 brown 100-chips
- Blind/dealer assignment: dealer and small blind are the opponent, big blind is the robot
- Robot-held card recognition: one card is `Qd`; the second hole card is unreadable
- Chip inventory recognition: subagent reported `my_chips` as red 6, blue 3, green 1, brown 0 and `opponent_chips` as red 3, blue 5, green 2, brown 3

## Decision

- No robot action was executed.
- I did not invoke Texas Hold'em strategy reasoning because the scene was not stable enough to justify committing an action.

## Validation Notes

- The scene stability subagent compared `s37/00_capture.jpg` against `s36/00_capture.jpg` and flagged significant robot-arm movement.
- The current frame is therefore treated as perception-only output for this step.
