# Eval Report

## Result
Perception step completed for `s30` using split visual subagents only.

## Evidence Merged
- Turn detection: it is our turn.
- Scene stability: unstable, because the robot arm is still interacting with
  chips.
- Blind buttons: dealer/opponent, small blind/opponent, big blind/robot, with
  partial confidence because the dealer button was inferred.
- Community cards: two cards visible, first uncertain `Jh`, second unreadable
  red-suit card.
- Held card: no readable robot-held hole card.
- Chip inventory: robot and opponent visible chip counts recorded from the
  capture.
- Bet counts: both betting areas had partially occluded counts.
- Robot behavior: active chip-manipulation pose, no obvious safety failure.
- Showdown: not active; no win/lose evidence.

## Notes
- Main-agent image perception was not used.
- No robot actions were executed.
- The output directory contains raw evidence files under
  `visual_raw/` for each invoked visual subagent.
