# Perception Run Report

Run ID: `p34_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`

## Outcome

The current DexHoldem perception step was completed using split visual subagents only. No robot action was executed.

## Merged Evidence

- Turn state: it is our turn.
- Board: `Qh`, `7d`, `6s`, `4c`.
- Hole cards: no robot-held hole card is visible.
- Buttons: dealer and small blind are on the opponent side; big blind is on the robot side.
- Chip inventory: partially visible and partially occluded; counts were recorded from the chip agent but should be treated as medium-confidence only.

## Reasoning Agent

The visible reasoning agent was requested, but it failed because the inherited model is not supported in this environment. No poker action recommendation was produced, and no action was committed.

## Verification

- Requested output directory exists.
- `visual_raw/` contains real evidence files.
- `visual_summary.json` was written.
- `eval_report.md` was written.
