# Eval Report

Perception-only pass completed for `p19_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low`.

## What I used

- Visual evidence from `s17/00_capture.jpg`
- Visual evidence from `s18/00_capture.jpg`
- Local run metadata from `action_sequence.json` and `runs/p19_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low/harness_prompt.md`

## Outcome

- No robot action was executed.
- Raw visual evidence was written to `runs/p19_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low/visual_raw/visual_agent.md`.
- Summary was written to `runs/p19_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low/visual_summary.json`.

## Reasoning subagent note

The visible reasoning subagent could not be used because the runtime rejected the inherited model for that agent type in this environment. I validated locally from the run context that no Texas Hold'em action reasoning was required for this perception-only step, so no action was committed.

## Visual readout

- `s17` shows a visible held `5♥`, five face-down community cards, dealer/big blind/your-turn markers, and robot occlusion near the lower-right seat area.
- `s18` shows five face-down community cards, two face-down near-player hole cards, the same table markers, and the robot hand hovering over the lower-right chip stacks.
- Both captures appear stable enough for perception, with uncertainty mainly from occlusion and face-down cards.
