# DexHoldem Perception Report

State: `s22`

## Outcome
Perception completed from the current frame using the visible visual subagent. No robot actions were executed.

## Evidence Summary
- The table is in normal orientation and the scene appears stable.
- No held cards are clearly visible in the current frame.
- No community cards are confidently identifiable.
- A `Your Turn` chip is visible near the lower-left/center area.
- Several chip stacks are visible, but exact counts are not confidently readable.
- The robot arm is extended over the right side of the table and appears poised to manipulate chips or cards.

## Reasoning Check
The visible reasoning subagent confirmed that no poker-action reasoning is needed because the current step is `recover_cached_action`, not `choose_poker_action`.

## Notes
- Raw evidence is stored in `visual_raw/visual_agent.md`.
- Summary JSON is stored in `visual_summary.json`.
