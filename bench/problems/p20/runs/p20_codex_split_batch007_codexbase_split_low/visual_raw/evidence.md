# Visual Evidence

- `scene_stability_agent`: Unstable. Compared `s17/00_capture.jpg` and `s18/00_capture.jpg`. The robot hand is still posed around a card on the right side and has not fully returned to idle.
- `turn_detection_agent`: It is our turn. The white "Your Turn" button is visible near the bottom-left robot seat area.
- `community_cards_agent`: No community cards are visible. The community-card row shows five face-down cards, and none of the shared board cards are face-up or readable.
- `bet_recognition_agent`: Opponent current bet: 3 red, 4 blue, 1 green, 2 brown. Some chips on the right side are partially blocked, so the green and brown counts are uncertain. Player current bet: 4 red, 3 blue. A couple of chips near the lower right are obscured by the robot hand, so there may be more there, but not confidently countable.
- `chip_recognition_agent`: Robot/player inventory is about 4 red 5-chips, 4 blue 10-chips, 2 green 50-chips, and 2 brown 100-chips, with green and brown counts uncertain due to occlusion. Opponent inventory is about 3 red 5-chips, 4 blue 10-chips, 4 green 50-chips, and 4 brown 100-chips, with green and brown counts approximate.
- `blind_button_recognition_agent`: Dealer button is at the opponent seat. The opponent is the small blind, and the robot is the big blind.
- `held_card_recognition_agent`: No readable held card is visible. The robot hand is present on the right side, but no card face is clearly readable.
- `robot_behavior_agent`: The dexterous hand is on the lower-right/robot side of the table, over the robot-side chip and hole-card area. It appears to be lifting or holding a card face-up, so the view-card action is still in progress.
