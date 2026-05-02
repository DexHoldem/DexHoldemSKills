# Eval Report

## Outcome

Perception step completed for the current capture using subagent evidence only.

## Verification

- Output directory: `runs/p43_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low`
- Raw evidence directory exists and is non-empty.
- Requested outputs are present:
  - `visual_raw/`
  - `visual_summary.json`
  - `eval_report.md`

## Merged Evidence

- The scene appears stable.
- `is_my_turn` is supported by the visible `Your Turn` disc.
- Hole cards are visible as `9d` and `5d`.
- Four community cards match the parsed state clearly.
- One community card is uncertain; a visual subagent read it as `8h` instead of parsed `Qh`.
- Chip and bet quantities are not reliably readable from this frame alone.

## Notes

- No robot actions were executed.
- No image perception was performed in the main agent; the result is merged from visual subagents.
