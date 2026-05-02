# Eval Report

## Result

Current perception state is stable and shows a visible showdown. The best merged interpretation is `show_hand`, not a confident `win` or `lose`.

## Evidence

- Scene stability is confirmed by the scene stability agent.
- Robot behavior is stationary and near rest, with no visible chip collection or unsafe manipulation.
- Community cards are visible and read most clearly as `K?`, `K?`, `4c`, `As`, `J?`.
- Robot hole cards are visible as `Kc` and `2s`.
- Opponent hole cards are visible, but only one card is confidently readable as `J`; the other remains ambiguous.
- Bet chips are visible in both betting areas, with some occlusion and overlap.
- Chip inventory appears to be approximately:
  - Robot: `5x2`, `10x2`, `50x0`, `100x2`
  - Opponent: `5x3`, `10x2`, `50x3`, `100x1`

## Merged Judgment

- `scene_stable`: true
- `showdown_visible`: true
- `recommended_loop_stage`: `show_hand`
- `do_not_execute_robot_actions`: true

## Notes

- The board and showdown agent are consistent that the table is at showdown, but the exact winner is not safely derivable from the image alone.
- The visual summary intentionally follows the current capture, even where it differs from older cached parsed state artifacts.
