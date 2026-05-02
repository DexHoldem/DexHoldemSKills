# DexHoldem Perception Report

## Outcome

Perception completed for `s48` using visible subagents only. No robot actions were executed.

## Key Readouts

- Scene stability: `false`
- Turn: `true`
- Buttons: dealer `opponent`, small blind `opponent`, big blind `robot`
- Community cards: `Qs`, `Qh`, `7d`, `Qc`, `4c`
- Board stage: `river`
- Robot-held cards: no exposed card detected by the held-card agent
- Bets:
  - Robot-side bet area: `10 x 1`, `50 x 1`
  - Opponent-side bet area: `5 x 4`, `50 x 1`, `100 x 1`
- Robot behavior: arm extended over the table; currently executing or paused mid-action
- Showdown state: `clear_loss` from the showdown agent

## Raw Evidence

Raw evidence files were written under `visual_raw/`:

- `scene_stability.json`
- `turn_detection.json`
- `blind_button.json`
- `community_cards.json`
- `held_cards.json`
- `bet_counts.json`
- `robot_behavior.json`
- `showdown_outcome.json`

## Notes

- Chip inventory was recovered after the first wait and is included in `visual_summary.json`.
- The board is already on the river, so no action reasoning was needed and no robot action was committed.
