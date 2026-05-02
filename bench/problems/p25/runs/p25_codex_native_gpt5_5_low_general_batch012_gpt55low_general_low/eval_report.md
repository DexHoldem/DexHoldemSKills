# Eval Report

State `s23` was processed as a visual parsing step only.

## Evidence

- `scene_stable`: true
- `is_my_turn`: true
- `community_cards`: no face-up board cards visible; five board cards appear face-down
- `my_current_bet`: one visible blue 10-chip on the robot side
- `opponent_bet`: not reliably separable from opponent inventory because of occlusion

## Raw Evidence

The raw visual evidence was written to:

- `runs/p25_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low/visual_raw/visual_agent.md`

## Notes

- The visible reasoning subagent could not be used successfully because the inherited-model configuration is not supported in this environment.
- No robot actions were executed.
