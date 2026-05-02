# DexHoldem Perception Report

## Result

Perception step completed from the local capture at `s45/00_capture.jpg`.

## Merged Evidence

- Scene stability: stable
- Turn detection: it is the robot/player turn
- Community cards: `10s`, `Qh`, `7d`, `6s`, `Jc`
- Blind buttons: dealer/opponent, small blind/opponent, big blind/robot
- Bets:
  - My current bet: `4 red`, `3 blue`, `0 green`, `0 brown`
  - Opponent bet: `2 red`, `4 blue`, `2 green`, `2 brown`
- Chips:
  - My chips: `4 red_5`, `4 blue_10`, `1 green_50`, `0 brown_100`
  - Opponent chips: `8 red_5`, `6 blue_10`, `3 green_50`, `2 brown_100`

## Confidence Notes

- Highest-confidence finding: `is_my_turn = true`
- Lowest-confidence finding: bet counts, due to overlap and partial occlusion
- The scene appears stable enough for perception, but a foreground robot arm could still introduce ambiguity across frames

## Action Status

- No robot action was executed
- No poker decision was committed in this step
