# Eval Report

## Result

Current perception step completed from the local capture at `s17/00_capture.jpg`.

## Merged Visual Evidence

- Scene is stable enough to continue.
- It is our turn.
- Robot hand is still in progress, extended into the play area, and holding a card.
- Held card is `5d`.
- No community cards are visible.

## Output Files

- `runs/p17_codex_split_batch007_codexbase_split_low/visual_raw/scene_stability_agent.md`
- `runs/p17_codex_split_batch007_codexbase_split_low/visual_raw/turn_detection_agent.md`
- `runs/p17_codex_split_batch007_codexbase_split_low/visual_raw/robot_behavior_agent.md`
- `runs/p17_codex_split_batch007_codexbase_split_low/visual_raw/held_card_recognition_agent.md`
- `runs/p17_codex_split_batch007_codexbase_split_low/visual_raw/community_cards_agent.md`
- `runs/p17_codex_split_batch007_codexbase_split_low/visual_summary.json`
- `runs/p17_codex_split_batch007_codexbase_split_low/eval_report.md`

## Constraints Observed

- No robot actions were executed.
- The main agent did not perform image perception directly; it merged subagent evidence only.
