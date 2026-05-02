# Eval Report

## Perception Result

- State: `s0`
- Scene stability: not stable enough to treat as settled for a clean next-step transition
- Turn ownership: it appears to be our turn

## Evidence Summary

- A visible white `Your Turn` marker is present near the lower-left robot seat.
- The table is mid-hand: no community cards are on the board, and chip stacks / face-down cards are already in play.
- One visual subagent judged the frame stable from a single still, but the second subagent judged the scene mid-hand rather than settled. I merged the evidence conservatively and marked the scene as not settled.

## Notes

- No robot actions were executed.
- Raw evidence was written to `runs/p1_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low/visual_raw/visual_agent.md`.
