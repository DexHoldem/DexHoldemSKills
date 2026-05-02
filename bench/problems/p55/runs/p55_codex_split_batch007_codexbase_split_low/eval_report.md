# DexHoldem Perception Report

Run: `p55_codex_split_batch007_codexbase_split_low`
State: `s0`

## Summary

The scene appears stable, but the turn state is not safely identifiable from the capture. The board is in a showdown-like presentation with community cards visible, yet the hand outcome is not resolved because both hole-card sides remain unreadable.

## Visual Findings

- Scene stability: stable.
- Turn detection: no reliable turn indicator or action prompt visible.
- Blind/button assignment: robot is dealer and small blind; opponent is big blind.
- Community cards: `3s`, `3c`, `5h`, `Tc`, with one leading card unreadable/face-down.
- Betting areas:
  - Top: `3x red 5`, `4x blue 10`, `1x green 50`, brown stack uncertain.
  - Bottom: `3x red 5`, `2x blue 10`, `1x green 50`, `1x brown 100`.
- Chip inventory:
  - Robot/player: `red 3`, `blue 2`, `green 1`, `brown 1`.
  - Opponent: `red 4`, `blue 5`, `green 2`, `brown 1`, plus `1` partially occluded white/unknown stack.
- Held card: no readable robot-held hole card.
- Robot behavior: hand is mid-action above the felt, but visually safe and not in a recovery state.
- Showdown: board visible, but no clear win/lose evidence.

## Notes

- Blind/button assignment was not available in a completed usable response.
- No robot action was executed.
- The main agent did not perform direct image perception; this report merges subagent evidence only.
