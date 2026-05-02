## chip_recognition_agent

Assuming the bottom seat is robot/player and the top seat is opponent:

- Robot/player inventory: `1 red`, `1 blue`, `1 green`, `1 brown` visible; `2` chips near the big blind marker are a bit ambiguous and could be inventory or part of the live action.
- Opponent inventory: `4 red`, `3 blue`, `0 green`, `0 brown` clearly visible on the left/middle rail area, plus `1 blue`, `2 green`, `2 brown` in the right cluster that is partially obscured by the robot arm.

Uncertain / not countable:
- The top-right mixed cluster is partially blocked, so exact counts there are not reliable.
- I excluded the `Your Turn` chip, the `DEALER` button, the `BIG BLIND` button, and all chips next to the face-up board cards as current bets/pot.

Confidence: low-medium on exact inventory counts, high on the excluded buttons/bets.
