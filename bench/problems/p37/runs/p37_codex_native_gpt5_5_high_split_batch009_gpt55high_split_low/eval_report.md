# Eval Report

## Result

Perception step completed for `s35` using subagent evidence only.

## Observations

- Capture file used: `s35/00_capture.jpg`
- Scene stability: unstable
- Turn state: robot/player turn
- Community cards: `Qs`, `8h`, `7d`, and a partially occluded `6c`
- Robot bet area: red 0, blue 2, green 1, brown 2
- Opponent bet area: red 2, blue 5, green 0, brown 0
- Dealer/small blind: opponent
- Big blind: robot

## Constraints Followed

- No robot actions were executed.
- No image perception was performed in the main agent.
- Independent visual subagents were run in parallel and their outputs were merged.

## Notes

- `visual_raw/` contains real evidence files from the subagents.
- The scene was marked unstable by one visual reader, so the report does not advance to action execution.
