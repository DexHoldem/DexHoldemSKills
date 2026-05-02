# Eval Report

Current perception pass for state `s36`.

## Evidence
- Robot behavior: the hand is extended over the center-right table area and appears mid-action rather than at rest.
- Community cards: five cards are visible. Readable cards are `Qs` and `Qh`; the remaining three are partially occluded or unreadable.
- Blind buttons: opponent is dealer and small blind; robot is big blind.
- Held card: no readable robot-held card.

## Assessment
- `scene_stable`: false
- `is_my_turn`: not established from the validated turn evidence
- `requires_human_help`: true

The current sequence already indicates a blocked human-help state, and the perception pass does not provide evidence for a robot action.
