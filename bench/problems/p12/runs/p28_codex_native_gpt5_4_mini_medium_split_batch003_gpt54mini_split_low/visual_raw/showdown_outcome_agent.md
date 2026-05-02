This is not showdown state.

- Opponent hole cards: not face-up; no readable opponent card values.
- Robot hole cards: not face-up; they would need cache if showdown later became relevant, but no cache is available from this capture.
- Community cards: some face-up board cards are visible, but the board is partially occluded and not enough to compare complete hands.
- Fold evidence: none visible.
- Win/lose evidence: none visible.

The visible `Your Turn` marker also suggests action is still pending, not a completed showdown. Recommended loop-stage label: do not mark `show_hand`, `win`, or `lose` yet; keep waiting for a clearer state.
