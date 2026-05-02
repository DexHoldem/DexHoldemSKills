# DexHoldem Perception Report

Run: `p62_codex_split_batch007_codexbase_split_low`
State: `s1`

## Result

- The table is on our turn.
- The scene is not clearly stable.
- Community cards visible: `4c`, `Ac`, `Jd`.
- Robot-held hole card is unreadable.
- No clear showdown outcome is present.

## Visual Notes

- Turn detection: the `Your Turn` marker is visible.
- Blind/button layout: dealer is on the opponent side; small blind maps to robot side; big blind is on the lower-middle/right side.
- Robot behavior: the arm is extended over the play area and appears mid-reach.
- Chip inventory: only partial, low-confidence inventory counts are available from the visual pass.

## Router Implication

This perception step does not commit a Texas Hold'em action. The visual evidence is sufficient to continue the state pipeline, but action reasoning was not required for this writeout.
