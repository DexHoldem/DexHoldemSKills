# DexHoldem Perception Report

State: `s17`

## Result

Merged the visible subagent evidence for the current capture and wrote it to `visual_summary.json`.

## Key Findings

- Scene is unstable; the robot hand is still in the play area and occluding a card.
- It is our turn, based on the visible `Your Turn` button.
- Dealer and small blind are on the opponent side; big blind is on the robot side.
- No community cards are face up; all five board positions are face-down.
- Robot-held visible hole card reads as `3d`.
- Chip counts were estimated from the visual subagent, with some occlusion-related uncertainty.

## Raw Evidence

- `visual_raw/s17_subagent_evidence.txt`

## Notes

- No robot actions were executed.
- No image perception was performed in the main agent; all visual claims were merged from subagents only.
