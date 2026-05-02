# Perception Run

Source state: `s0`
Source capture: `s0/00_capture.jpg`

## Result

- Scene stable: yes
- Our turn: no
- Community cards: one unreadable card back, then `3s`, `3c`, `5h`, `Tc`
- Dealer / blinds: dealer at robot seat, small blind at robot seat, big blind at opponent seat
- Robot-held card: visible but unreadable due to occlusion
- Robot behavior: hand is extended over the opponent-side betting area, motion is still in progress, but no clear safety issue

## Chips And Bets

- Robot inventory: about `3x 5`, `2x 10`, `1x 50`, `2x 100`
- Opponent inventory: about `3x 5`, `5x 10`, `1x 50`, `4x 100`
- Robot current bet: `3x 5`, `2x 10`, `1x 100`
- Opponent current bet: `3x 5`, `4x 10`

## Action Handling

- No robot action was executed.
- The reasoning subagent was not invoked because the router condition for a Texas Hold'em action decision was not met: it is not our turn.
