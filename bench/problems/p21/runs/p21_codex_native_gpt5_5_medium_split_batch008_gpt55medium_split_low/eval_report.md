# DexHoldem Perception Report

Run: `p21_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`
State: `s18`
Frame: `s18/00_capture.jpg`

## Summary
The current perception step indicates:
- No readable community cards.
- It is not our turn.
- The scene is not stable enough to treat as settled.
- Dealer and small blind are on the opponent side; big blind is on the robot side.
- No clearly countable current bet chips are visible in either betting area.
- The robot-held hole card is readable as `5d`.
- The robot hand is active in the lower-right play area and not in a clear rest pose.

## Notes
- This was perception only. No robot actions were executed.
- The main agent did not perform image interpretation; the report merges returned subagent evidence only.
- Raw evidence files were written under `visual_raw/` for the called subagents.
