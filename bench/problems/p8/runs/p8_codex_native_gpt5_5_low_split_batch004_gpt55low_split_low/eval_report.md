# DexHoldem Perception Step

Source capture: `s6/00_capture.jpg`

## Conclusion

The scene is still acting, not settled. The robot hand is in the middle of putting the left hole card back down, so this perception step should not advance to a new robot action yet.

## Merged Evidence

- Scene stability: unstable because the latest frame still shows the robot holding the card in midair.
- Robot behavior: the hand is extended over the table and still holding the left hole card; the `put_down_card` action is in progress.
- Turn detection: it is our turn.
- Community cards: five board positions are visible, but all are face down / unreadable.
- Held card: a partially exposed card is still visible in the gripper, but it is unreadable.
- Blind buttons: dealer button appears on the opponent side; blind assignment is inferred as dealer/opponent, small blind/opponent, big blind/robot under the two-player rule.
- Chips: robot and opponent inventory counts were estimated, with some occlusion uncertainty on the right-side stacks.

## Result

Do not execute robot actions. Wait for a later capture that shows the hand near rest pose and the card fully returned before updating the step state.

