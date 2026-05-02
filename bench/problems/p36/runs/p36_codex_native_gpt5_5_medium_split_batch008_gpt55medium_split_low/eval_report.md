# DexHoldem Perception Report

- State: `s33`
- Capture: `s33/00_capture.jpg`
- Scene stable: yes
- Turn: yes, it is the robot/player turn
- Community cards: `Ts, 3h, 7d, 9s, Ac`
- Dealer: opponent
- Small blind: opponent
- Big blind: robot

## Evidence Summary

The visual subagents agreed that the scene is stable enough to read. The community board is complete and clearly visible. The robot/player turn indicator is visible as a physical `Your Turn` button near the lower-left side of the table.

The robot-held hole card was not clearly visible in the capture. Bet counts in both betting areas were not reliable enough to record as exact values, so they are left null in the summary.

Inventory chip counts were recovered from the dedicated chip-recognition subagent:

- Robot inventory: red 5 = 6, blue 10 = 3, green 50 = 3, brown 100 = 4
- Opponent inventory: red 5 = 3, blue 10 = 5, green 50 = 3, brown 100 = 2

## Output Status

- `visual_raw/` contains a real evidence file: `evidence.json`
- `visual_summary.json` written
- `eval_report.md` written
