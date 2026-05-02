# Evaluation Report

Run: `p46_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low`

Source image: `s45/00_capture.jpg`

## Merged Evidence

- Turn detection: it is our turn. The white turn button is visible and readable as `Your Turn`.
- Scene stability: stable enough to continue from the single frame, with normal uncertainty because no prior frame was provided.
- Community cards: `Qs`, `Qh`, `7d`, `6s`, `7c`.
- Bets: robot/player current bet `red=4, blue=1, green=0, brown=0`; opponent current bet `red=0, blue=1, green=3, brown=2`.
- Blind buttons: dealer on opponent side, small blind opponent, big blind robot.
- Held card read: no readable robot-held hole card from the dedicated held-card worker.
- Robot behavior: hand is hovering over the right side of the table, no clear grasp or placement, no safety issue visible.
- Showdown evidence: a later visual worker reported face-up hole cards and concluded the hand appears tied, with `show_hand` as the recommended stage label.

## Assessment

The visual evidence is internally consistent enough to say the scene is stable, it is our turn, and the board is fully visible. The bet-recognition output is partial but usable for the visible chips. The showdown worker introduced a higher-level interpretation that the image may correspond to a tied show-hand state rather than a normal in-hand action.

No robot action was executed.

## Output Verification

- `runs/p46_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_raw/` exists
- `runs/p46_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_summary.json` exists
- `runs/p46_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/eval_report.md` exists
- `visual_raw/` is non-empty
