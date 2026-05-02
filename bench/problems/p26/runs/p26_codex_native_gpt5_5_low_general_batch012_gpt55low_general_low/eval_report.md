# DexHoldem Perception Report

## Run

- `run_id`: `p26_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low`
- `state`: `s23`
- `capture`: `s23/00_capture.jpg`

## Evidence

Visual subagents were run in parallel and provided the following merged evidence:

- The scene is stable and usable for perception.
- The camera is angled from the near/bottom side of the table toward the far/top player.
- The red `TEXAS HOLD'EM` mat provides clear orientation cues.
- The right side of the frame is partially occluded by the robot/camera assembly.
- Only face-down cards are visible; no hole-card or community-card ranks/suits are readable.
- Chip denominations `5`, `10`, `50`, and `100` are visible, but exact stack membership and total bet amounts are not reliable because of overlap and occlusion.

## Reasoning Subagent

I attempted to invoke the visible reasoning subagent, but the environment rejected the inherited-model path for that agent. No poker action was committed from this step.

## Conclusion

This is a valid perception frame, but not a fully reliable card/bet parsing frame. The safest output is stable-scene evidence with explicit uncertainty on cards and bets.
