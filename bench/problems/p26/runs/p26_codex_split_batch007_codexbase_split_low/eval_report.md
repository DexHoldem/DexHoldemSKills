# Perception Report

- Latest frame: `s23/00_capture.jpg`
- Scene stability: stable
- Turn state: it is our turn
- Community cards: none visible; board cards are face down
- Robot-held hole cards: unreadable
- Blind/dealer buttons: visible but seat assignment is unclear
- Showdown state: not showdown

## Evidence Summary

The scene is visually settled compared with `s22/00_capture.jpg`. The robot arm is still extended over the right side of the table, but the robot-behavior agent did not find active motion or failure evidence.

The turn-detection agent reported the white `Your Turn` button near the lower-left player seat, so the table is currently actionable from a turn perspective. Community cards remain face down and no held cards are readable, so there is no new hand-content evidence to merge.

Bet and chip-recognition outputs are consistent with a normal preflop / early-hand table state, with some occlusion on the right side of the image. Showdown evidence is absent.

## Result

Perception step completed without executing any robot action.
