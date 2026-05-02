# DexHoldem Perception Report

Current state: `s17`

The frame is **unstable**. The robot dexterous hand is still over the robot-side hole-card / chip area and is visibly holding a card, so the `view_right_hole_card` sequence has not visually settled yet. There is no clear physical failure, but this is not an idle/rest pose and should be treated as still in progress.

Key reads:

- Turn: it is our turn.
- Community cards: none visible; all five board positions are face down/unreadable.
- Held card: `5d` is readable in the gripper.
- Blind buttons: opponent seat has dealer and small blind; robot seat has big blind.
- Chip inventory: robot inventory and opponent inventory were counted from visible stacks only; chips near the hand were excluded because they look like active bet chips or are occluded.

Recommendation from merged evidence: **wait and recapture**, not a new robot action.
