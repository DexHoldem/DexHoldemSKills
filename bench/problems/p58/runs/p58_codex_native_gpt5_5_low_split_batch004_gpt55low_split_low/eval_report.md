# DexHoldem Perception Report

- Run: `p58_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low`
- Capture: `s0/00_capture.jpg`
- Stage: `win`
- Current step: `collect_winnings`

## Consolidated Read

- The scene is visually stable enough to continue, but the stability call is limited because no previous capture was available in this workspace snapshot.
- The turn/ownership read says it is our turn, based on the visible white button at the robot/bottom seat.
- Community cards read as `Jh`, `Ac`, `Ks`, `4c`, `Kd`.
- Held cards are not visibly present in the robot hand in this frame.
- Dealer and small blind are assigned to the robot; big blind appears to be on the opponent side.
- Robot current bet lane: `4x red (5)` chips visible.
- Opponent current bet lane: `4x red (5)`, `5x blue (10)`, plus possibly `2x green (50)` and `2x brown (100)` with occlusion uncertainty.
- Remaining inventory reads are partially occluded but available in the raw evidence files.
- Robot arm is extended over the right side of the table and does not look fully idle, so execution stability should be treated cautiously.

## Actions

- No robot action was executed.
- Perception evidence was merged only from the visible subagents.
