# DexHoldem Perception Report

Latest state: `s7`

## Summary

The scene is not stable enough to advance with confidence. The robot hand remains extended over the lower-right table area, which occludes part of the robot-side hole-card and betting region.

## Parsed Visual Facts

- Turn: it is our turn.
- Community cards: none visible.
- Blind buttons: dealer is at the opponent seat; opponent is small blind; robot is big blind.
- Robot hole card: no safely readable held card.
- Chips:
  - Robot/player inventory: 4 red `5`, 4 blue `10`, 0 green `50`, 0 brown `100`.
  - Opponent inventory: 4 red `5`, 4 blue `10`, 4 green `50`, 4 brown `100`.
- Robot behavior: the hand is extended and paused low over the felt; no obvious failure is visible.

## Decision

No robot action was executed. The visual state is unresolved for motion-sensitive follow-up because the scene is still conservatively marked unstable.

## Evidence Notes

- The board read from the community-card agent is empty.
- The held-card agent found no safely readable held card.
- The showdown agent did not support `show_hand`, `win`, or `lose`.
