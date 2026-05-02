# DexHoldem Perception Report

Run: `p3_codex_split_gpt54mini_isolated_fasttest_004`

## Result

Perception was not recoverable from the available session context. No scene image or readable resource was exposed to the visual agents, so the table state could not be verified.

## Agent Evidence

- Turn detection: turn button not safely identifiable.
- Scene stability: unstable or unavailable due to no accessible captures.
- Dealer / blinds: unclear.
- Community cards: unreadable.
- Robot hole card: unreadable.
- Betting areas: inaccessible.
- Chip inventory: inaccessible.
- Reasoning: fallback state is `perception_unavailable`; do not recommend or commit any poker action.

## Conclusion

No action should be taken from this run. The correct fallback is to wait for a valid capture with visible turn, dealer/blind markers, cards, bets, and chip counts.
