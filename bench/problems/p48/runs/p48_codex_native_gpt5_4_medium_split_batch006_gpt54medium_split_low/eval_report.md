# DexHoldem Perception Report

Current loop stage: `atom_idle`

## Result

- `scene_stable`: `false`
- `is_my_turn`: `true`
- Community cards: `Ts, 8h, 7d, 6s, Jc`
- Blind assignment: dealer/opponent, small blind/opponent, big blind/robot

## Bets

- `my_current_bet`: 1 blue chip, 1 green chip
- `opponent_bet`: 2 red chips, 1 green chip, 1 brown chip

## Inventory

- `my_chips`: 4 red, 3 blue, 2 green, 6 brown
- `opponent_chips`: 2 red, 5 blue, 1 green, 2 brown

## Notes

- The scene-stability agent judged the frame unstable because the robot hand is still changing pose and the chip area on the upper-right is still being redistributed.
- Because the scene is unstable, I did not invoke Texas Hold'em action reasoning or any robot actions.
- The output files were written to the exact requested run directory with no extra suffix.
