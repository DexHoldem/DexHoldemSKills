# Eval Report

Current perception step completed from subagent evidence only.

## Outcome

- Scene is not stable enough to continue.
- It is the player's turn.
- Community cards are not visible.
- Dealer is the opponent; in heads-up play that also makes the opponent the small blind and the robot the big blind.
- Robot behavior is consistent with an in-progress manipulation phase, not an idle pose.
- No robot-held hole card is readable.

## Validation

- A Texas Hold'em reasoning subagent was attempted, but the environment rejected it because the inherited model mode is unsupported for this account.
- No poker action was committed.

## Files Written

- `runs/p10_codex_native_gpt5_4_medium_split_batch006_gpt54medium_split_low/visual_raw/`
- `runs/p10_codex_native_gpt5_4_medium_split_batch006_gpt54medium_split_low/visual_summary.json`
- `runs/p10_codex_native_gpt5_4_medium_split_batch006_gpt54medium_split_low/eval_report.md`
