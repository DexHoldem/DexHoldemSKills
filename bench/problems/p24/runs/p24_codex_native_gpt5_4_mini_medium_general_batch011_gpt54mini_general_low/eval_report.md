# DexHoldem Perception Eval Report

Run: `p24_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low`

## Outcome

The latest capture was merged from two visual subagents only. The main agent did not perform image perception and did not execute any robot actions.

## Merged Evidence

- `s21/00_capture.jpg` shows the robot hand extended across the lower/table area.
- One visual pass judged the scene stable enough by comparing `s20` and `s21` and found no visible blur or rearrangement.
- Another visual pass noted that the table area is still partially occluded and that hole cards are not readable in the frame.
- A white round `Your Turn` marker is visible near the robot side.
- No community cards are visibly parseable.
- No dealer, small blind, or big blind button is clearly readable.

## Interpretation

The safest perception result is `wait` for the current step: the frame has some stability evidence, but the core poker fields remain insufficiently visible for a confident state update.

## Outputs Written

- `runs/p24_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/visual_raw/visual_agent.md`
- `runs/p24_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/visual_summary.json`
- `runs/p24_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low/eval_report.md`
