# Visual Eval Report

- `scene_stable`: true
- `loop_stage`: `to_recover`
- `is_my_turn`: true
- `blind`: `none`
- `community_cards`: none visible
- `my_chips`: `5: 3, 10: 3, 50: 0, 100: 0`
- `opponent_chips`: `5: 4, 10: 4, 50: 0, 100: 0`
- `my_current_bet`: `5: 3, 10: 3, 50: 0, 100: 0`
- `opponent_bet`: `5: 3, 10: 3, 50: 0, 100: 0`
- `showdown_outcome`: `not_showdown`

## Evidence

- Scene stability agent reported `s_current/00_capture.jpg` and `s21/00_capture.jpg` are visually unchanged.
- Robot behavior agent reported the arm is still extended over the table, safe, retryable, and not near rest.
- Turn detection agent reported the on-table marker says `Your Turn`.
- Blind button agent reported `none`.
- Community cards agent reported no clearly visible board cards.
- Chip agent reported robot inventory `5: 3, 10: 3, 50: 0, 100: 0` and opponent inventory `5: 4, 10: 4, 50: 0, 100: 0`.
- Bet agent reported robot current bet `5: 3, 10: 3, 50: 0, 100: 0` and opponent current bet `5: 3, 10: 3, 50: 0, 100: 0`.

## Notes

- `loop_stage` was inherited from the prior parsed state and kept as `to_recover` because the scene is stable, the robot pose remains in a retryable reach posture, and the workflow context still matches recovery rather than completed idle.
