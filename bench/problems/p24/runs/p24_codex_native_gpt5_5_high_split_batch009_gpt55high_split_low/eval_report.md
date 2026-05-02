# DexHoldem Perception Step

- State: `s21`
- Capture: `s21/00_capture.jpg`
- Loop stage: `to_recover`

## Evidence

- `scene_stability_agent`: unstable. The robot arm/end-effector was still extended over the table and the human hand appeared blurred or mid-motion.
- `robot_behavior_agent`: mid-action, hovering near the table, not a recovery state. No obvious collision, jam, dropped object, or human intervention was visible.
- `turn_detection_agent`: it is our turn. The white `Your Turn` button was visible and not meaningfully occluded.
- `reasoning_validator`: safest non-action outcome is `to_recover_pending_wait`.

## Outcome

The perception result is a non-action recovery hold: the scene is not settled enough to advance recovery as complete, so the correct outcome is to wait and re-evaluate rather than execute any robot action.

## Verification

- `visual_raw/` contains a real evidence file.
- `visual_summary.json` written.
- `eval_report.md` written.
