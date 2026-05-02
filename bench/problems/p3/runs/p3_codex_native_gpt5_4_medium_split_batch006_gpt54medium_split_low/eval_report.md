# Perception Step Report

Current frame: `s1/00_capture.jpg`
Previous frame: `s0/00_capture.jpg`

## Merged Evidence

- Scene stability: unstable. The robot arm moved significantly between `s0` and `s1` and is still extended into the play area.
- Turn detection: it is our turn. The white turn button is visible near the bottom-left robot seat.
- Held card recognition: no readable held card is visible.
- Robot behavior: the hand is extended over the right side of the table, empty, and not in an idle pose.
- Community cards: no face-up community cards are visible.
- Blind buttons: opponent seat has dealer and small blind; robot seat has big blind.
- Bet recognition: no visible current bets in either betting lane.
- Chip recognition: remaining chip inventory is not reliably readable from this frame.
- Chip recognition: bottom/robot-side inventory shows 4 red 5-chips and 4 blue 10-chips; top/opponent-side inventory shows 4 red 5-chips and 5 blue 10-chips. Higher denominations are not reliably readable because of occlusion.

## Conclusion

The scene is not settled enough to advance the perception loop as stable. The current evidence supports `is_my_turn = true`, but the robot is still in an active extended pose and the table view is partially occluded, so the safest state judgment is unstable.
