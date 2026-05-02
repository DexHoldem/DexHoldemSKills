# Perception Report

Captured state: `s0`

Summary:
- The frame is usable for perception.
- It is not the robot/player turn.
- Community cards read as `3s`, `3c`, `2d`, `Qc`.
- Visible bet values are `120` for both sides from the betting-lane counts returned by the visual worker.
- Button assignment is `dealer=robot`, `small_blind=robot`, `big_blind=opponent`.

Notes:
- The dedicated scene-stability worker returned an unreadable-frame failure, but the other scoped visual workers successfully read the same capture, so the merged result treats the scene as stable enough for perception.
- No robot action was executed.
- No poker-action reasoning subagent was needed because the router implication is to wait for the opponent.
