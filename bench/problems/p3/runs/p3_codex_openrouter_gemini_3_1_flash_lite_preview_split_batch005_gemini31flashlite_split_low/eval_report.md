# Eval Report

Perception pass completed without executing any robot action.

## Inputs Used

- Existing parsed state from `s0/01_parsed_state.md`
- Existing action record from `s0/02_action.md`
- Current capture path: `s1/00_capture.jpg`

## Outcome

- Scene judged stable.
- `Your Turn` marker is visible.
- Community cards are not visible.
- Both players' chip inventories remain at 4 stacks each of `5`, `10`, `50`, and `100`.
- Current bets are zero for both sides.
- Robot behavior is idle / near initial pose.
- Big blind marker is at the robot seat.

## Constraints And Limitations

- No robot action was executed.
- Dedicated visual subagents were not available in this runtime.
- The reasoning subagent request failed because its inherited model setting is unsupported in this environment.

## Notes

The output artifacts were written to the exact requested run directory:

- `runs/p3_codex_openrouter_gemini_3_1_flash_lite_preview_split_batch005_gemini31flashlite_split_low/visual_raw/`
- `runs/p3_codex_openrouter_gemini_3_1_flash_lite_preview_split_batch005_gemini31flashlite_split_low/visual_summary.json`
- `runs/p3_codex_openrouter_gemini_3_1_flash_lite_preview_split_batch005_gemini31flashlite_split_low/eval_report.md`
