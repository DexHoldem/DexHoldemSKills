# Visual Eval Report

- Current capture: `s0/00_capture.jpg`
- Scene is judged stable and the table is ready for the next decision.
- Physical turn marker says it is our turn.
- Blind assignment: robot is big blind, opponent is small blind.
- No community cards are visible.
- Robot hand is hovering/resting and not holding chips or a card.
- Inventory and bet counts were merged from the visual subagents.

## Evidence

- Scene stability: compared only against the current frame; no prior image was available to the stability worker.
- Turn marker: visible "Your Turn" indicator.
- Blinds: visible buttoning indicates opponent dealer/small blind and robot big blind.
- Robot inventory estimate: 5s=4, 10s=3, 50s=1, 100s=2.
- Opponent inventory estimate: 5s=4, 10s=5, 50s=1, 100s=3.
- Robot current bet estimate: 5s=4, 10s=3, 50s=1, 100s=2.
- Opponent current bet estimate: 5s=3, 10s=3, 50s=1, 100s=3.
