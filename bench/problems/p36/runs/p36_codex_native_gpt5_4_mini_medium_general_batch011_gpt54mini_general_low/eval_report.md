# DexHoldem Perception Step

## Outcome
The current perception step is complete. The merged evidence supports a stable river-state table with `Your Turn` visible and no visual indication of forced chip movement.

## Evidence
- [visual_raw/visual_agent.md](./visual_raw/visual_agent.md)
- The board shows five community cards.
- The clearest visible action cue is `Your Turn` at seat 6.
- A `BIG BLIND` marker is visible at seat 5.
- The right-side robot arm partially occludes the table, but it is not visibly manipulating cards or chips.

## Parsed-State Validation
- `scene_stable`: `true`
- `is_my_turn`: `true`
- Community cards: `Ts, Qh, 7d, 6s, Jc`
- My committed bet total: `260`
- Opponent committed bet total: `170`
- Call amount: `0`

## Recommended Poker Action
`check`

## Notes
- This run did not execute any robot actions.
- Raw evidence was written to `visual_raw/visual_agent.md`.
