# Perception Report

Current capture: `s_current/00_capture.jpg`

## Merged Evidence

- Scene stability: unstable; the robot arm is stretched across the table and the frame is still in progress.
- Turn state: it is our turn; the white turn button is visible near the bottom-left robot seat area.
- Community cards: one position is unreadable/face-down, then `8h`, `7d`, `6s`, `7c`.
- Held card: no readable held card is visible; the robot hand area is occluded.
- Blind buttons: dealer and small blind are on the opponent seat; big blind is on the robot seat.
- Robot behavior: the hand is moving/positioning rather than at rest; no obvious failure or recovery condition.
- Bet recognition: no returned evidence before timeout.
- Chip recognition: no returned evidence before timeout.

## Output Notes

- The raw evidence directory contains one file per called subagent.
- Because the scene is still in progress, the perception pass should be treated as unsettled even though turn ownership is readable.
