# DexHoldem Perception Step

## Result
- State: `s0`
- Scene stable: yes
- Turn: robot/player turn
- Dealer: robot
- Small blind: robot
- Big blind: opponent
- Community cards: `Kd`, `3s`, `3c`, `7h`, `Tc`
- Showdown outcome: loss

## Evidence
- Community cards came from the visual community-card subagent.
- Button assignment came from the blind/button subagent.
- Turn status came from the turn-detection subagent.
- Stability came from the scene-stability subagent.
- Loss determination came from the showdown-outcome subagent.

## Notes
- No robot actions were executed.
- The main agent did not inspect the image directly; this report merges subagent evidence only.
- Cached local state is consistent with a loss-hand cleanup flow.
