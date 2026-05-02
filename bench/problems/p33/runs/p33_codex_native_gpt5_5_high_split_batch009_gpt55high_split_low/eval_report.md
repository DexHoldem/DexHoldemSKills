# DexHoldem Perception Report

Run: `p33_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low`

## Outcome
The current perception step is unstable and consistent with the documented `request_human_help` branch.

## Evidence
- `scene_stability_agent` judged the scene **Unstable** after comparing `s30/00_capture.jpg` against `s29/00_capture.jpg` and `s28/00_capture.jpg`.
- `robot_behavior_agent` reported the robot hand extended over the right-side table area, away from rest pose, with no clear settled post-action state.
- `chip_recognition_agent` found the upper-right chip area disrupted and partly occluded, which supports the stuck-chip / chip-push disruption description.

## Notes
- No robot actions were executed.
- The main agent did not perform image perception directly; the summary merges only the subagent evidence.
- The requested output directory was used exactly as specified.
