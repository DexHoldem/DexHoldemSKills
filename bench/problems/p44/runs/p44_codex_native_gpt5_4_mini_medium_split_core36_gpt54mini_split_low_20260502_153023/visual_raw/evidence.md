# Visual Evidence

- Scene stability agent: `s41/00_capture.jpg` vs `s40/00_capture.jpg` showed the robot arm/gripper moving rightward and retracting; scene is unstable.
- Robot behavior agent: hand is retracting right, open/empty, not near rest, no safety issue, motion still in progress.
- Turn detection agent: `Your Turn` is readable and visible; it is our turn.
- Blind button agent: `big_blind`.
- Community cards agent: reported low-confidence partial read (`10c?`, `7d?`) that conflicted with durable prior board state.
- Chip recognition agent: robot inventory `5:4, 10:3, 50:0, 100:0`; opponent inventory `5:0, 10:1, 50:1, 100:2`.
- Bet recognition agent: robot current bet `5:4, 10:3, 50:0, 100:0`; opponent bet `5:1, 10:2, 50:0, 100:1`.
- Showdown outcome agent: `not_showdown`.
