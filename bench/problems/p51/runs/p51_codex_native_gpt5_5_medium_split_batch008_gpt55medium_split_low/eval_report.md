# DexHoldem Perception Step

- Run id: `p51_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`
- Source state: `s52`
- Raw evidence: `visual_raw/00_capture.jpg`

## Summary

The capture was parsed from subagent evidence only. The current scene is on our turn, but the robot arm is still extended over the table and appears to be in the middle of a chip interaction, so the scene is not stable enough to advance as a completed action.

## Key Evidence

- Turn detection: our turn, high confidence.
- Scene stability: unstable, because the robot arm/gripper is still over the betting area and contacting or pressing near chips.
- Robot behavior: action still in progress or settling.
- Community cards: 4 visible, reported as `Ts`, `Qh`, `7d`, and one unreadable spade card.
- Buttons/blinds: dealer opponent, small blind opponent, big blind robot.
- Bets: robot/player bet `blue=1, green=1`; opponent bet `blue=4, red=3`.
- Inventory chips: robot/player approximately `red=7, blue=3`; opponent approximately `red=2, blue=5`.

## Router Outcome

The router should remain in `wait` for the `acting` loop stage. No robot action was executed.
