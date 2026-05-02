# DexHoldem Perception Report

- Run: `p63_codex_native_gpt5_4_medium_split_batch006_gpt54medium_split_low`
- State: `s0`
- Loop stage: `win`
- Intent: `collect_winnings`
- Robot action executed: `false`

## Merged Perception

- Scene is stable enough to continue from a single-frame read.
- Robot arm is visible at the right edge, extended over the table, but appears idle/paused and not manipulating chips or cards.
- Community cards read as `Kd`, `Ks`, `Ac`, `As`, `Jd`.
- Blind/dealer assignment reads as dealer `opponent`, small blind `opponent`, big blind `robot`.
- Robot hole cards were not visibly readable from the capture.
- Showdown outcome reads as `robot_wins`.

## Chip Read

- My current bet: `red_5=2`, `blue_10=3`, `green_50=0`, `brown_100=2`
- Opponent bet: `red_5=2`, `blue_10=1`, `green_50=2`, `brown_100=2`
- My chips: `red_5=2`, `blue_10=4`, `green_50=0`, `brown_100=2`
- Opponent chips: `red_5=4`, `blue_10=2`, `green_50=3`, `brown_100=2`

## Router Handling

- The router does not need `choose_poker_action` for the current `win` stage.
- No robot action was committed.

## Notes

- All outputs were merged from visible subagents only.
- The visual read is based on a single capture, so stability is a frame-level judgment rather than a temporal one.
