# DexHoldem Perception Report

## Result

- Latest state: `s50`
- Scene stability: `false`
- Turn: `true`
- Recommended action: `wait`

## Visual Evidence

- Community cards worker read: `10s, 8d, 7d, 6s, 3c`
- Blind-button worker read: dealer is `opponent`
- Bet worker read: robot bet `{5:0,10:1,50:1,100:2}`, opponent bet `{5:2,10:0,50:1,100:1}`
- Chip worker read: robot inventory `{5:4,10:3,50:3,100:2}`, opponent inventory `{5:2,10:4,50:3,100:3}`
- Held-card worker read: robot hole cards `9d, 5d`
- Robot behavior worker read: `pull back 100`, `scene_stable: false`
- Scene stability worker read: `scene_stable: false`, `scene_changed: true`
- Showdown worker read: `opponent_win`

## Validation

- The reasoning subagent confirmed `wait` remains the correct recommendation because the robot motion is still in progress and the scene is not stable.
- No robot action was executed.

## Notes

- `visual_raw/` contains evidence files for each subagent.
- The fresh community-card read differs from the prior parsed state, so the report reflects the subagent evidence for this run.
