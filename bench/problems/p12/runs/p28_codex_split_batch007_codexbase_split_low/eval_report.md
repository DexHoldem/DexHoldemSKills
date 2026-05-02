# Perception Report

State: `s24`

## Verdict

The scene is **unstable**, so this is a perception-only step. I did not execute any robot action.

## Merged Evidence

- `scene_stable`: false
- `is_my_turn`: true
- `community_cards`: `7d`, `6s`
- `blind_buttons`: dealer and small blind at the opponent seat, big blind at the robot
- `robot_inventory`: about 4 red 5-chips and 3 blue 10-chips, with the blue count partly occluded
- `opponent_inventory`: about 2 red 5-chips, 1 blue 10-chip, 1 green 50-chip, and 4 brown 100-chips
- `held_card`: a card is present in the robot gripper, but it is unreadable
- `robot_behavior`: hand still in progress near the lower-right betting lane, not at rest

## Notes

- The turn button is visible and readable as `Your Turn`.
- The visual agents disagreed in one useful way: stability is not settled, while turn ownership is still identifiable.
- Because the scene is still changing, I did not call the reasoning agent or commit any action.
