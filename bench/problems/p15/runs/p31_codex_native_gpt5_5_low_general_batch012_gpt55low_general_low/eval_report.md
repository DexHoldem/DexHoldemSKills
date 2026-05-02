# DexHoldem Perception Report

- Run id: `p31_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low`
- Latest frame: `s30/00_capture.jpg`
- Compared frames: `s29/00_capture.jpg`, `s30/00_capture.jpg`

## Result

The scene is unstable. The visual subagent reported that the robot arm/hand
moved significantly between the two frames and has not fully settled.

## Evidence

- The robot hand is still in motion.
- Cards and chip stacks appear mostly unchanged.
- The turn button remains visible.
- The latest frame is not yet suitable for advancing the perception state.

## Output Status

- `visual_raw/` contains raw evidence.
- `visual_summary.json` written.
- `eval_report.md` written.
