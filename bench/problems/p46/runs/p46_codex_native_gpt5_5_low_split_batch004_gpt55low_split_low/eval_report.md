# DexHoldem Perception Step

- Run: `runs/p46_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low`
- State: `s45`
- Source capture: `s45/00_capture.jpg`

## Result

The scene is unstable, so no robot action should be executed.

## Merged Perception

- Scene stability: unstable because the robot arm is still moving across frames `s44` and `s45`.
- Turn detection: it is our turn.
- Community cards: `Qs`, `Qh`, `7d`, `6s`, `7c`.
- Bets:
  - My current bet area: `5: 0`, `10: 1`, `50: 1`, `100: 1` with some overlap uncertainty.
  - Opponent bet area: `5: about 5`, `10: 1`, `50: 1`, `100: about 2` with partial occlusion uncertainty.
- Robot behavior: the dexterous hand is still in progress over the lower-right chip area and has not returned to rest pose.

## Decision

- Do not commit an action.
- Wait for another settled capture before any poker or recovery decision.
