# DexHoldem Perception Report

- Capture: `s0/00_capture.jpg`
- Scene: stable
- Turn: our turn
- Loop stage: `show_hand`

## Visual Findings

- Community cards: 5 visible, read left to right as `Kd`, `Kc`, `Ac`, `As`, `Jd`, with the last three somewhat uncertain.
- Bets: both bet areas are visible, but the counts are approximate because of overlap and right-side occlusion.
- Chip inventory: both players' inventories are visible, approximate on the opponent side due to occlusion.
- Blind buttons: conflicting dealer/small-blind markers are visible, so the blind assignment is not cleanly identifiable. The robot seat clearly has the big blind marker.
- Robot behavior: the robot hand is still extended over the right side; visually safe, but not at rest.
- Showdown state: this looks like a showdown-like frame with face-up hole cards, but the hand result is not clear.
- Held cards: no robot-held hole card is safely readable.

## Merged Judgment

The safest merged parse is a stable showdown/show-hand frame with our turn indicator visible, but with unresolved blind assignment and approximate chip/bet counts. Because the showdown result is not confidently readable, I did not infer win or lose.

