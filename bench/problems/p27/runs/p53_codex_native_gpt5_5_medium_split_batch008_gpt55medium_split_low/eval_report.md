# DexHoldem Perception Eval Report

Run: `p53_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`
State: `s0`

## Perception Summary
- Scene stability: unstable
- Turn detection: it is our turn
- Blind buttons: dealer opponent, small blind opponent, big blind robot
- Community cards: 3 visible, read as `3c`, `7h`, `Qs` with some uncertainty
- Bets: my area has 2 red chips at 5 each; opponent area has 2 blue chips at 10 each
- Inventory: robot and opponent chip counts recorded in the raw evidence files
- Robot behavior: hand extended and action appears still in progress
- Showdown outcome: no clear showdown or win/lose outcome

## Notes
- The main agent did not inspect the image directly.
- Raw evidence is stored per subagent under `visual_raw/`.
- No robot action was executed.
