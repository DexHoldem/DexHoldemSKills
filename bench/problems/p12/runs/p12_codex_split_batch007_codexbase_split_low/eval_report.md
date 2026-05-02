# DexHoldem Perception Step

Current state: `s7`

## Outcome

The scene is unstable, and the robot hand is still mid-action. I did not execute any robot actions.

## Evidence

- `scene_stability_agent`: unstable when comparing `s6/00_capture.jpg` and `s7/00_capture.jpg`
- `robot_behavior_agent`: hand extended over the right side, mid-action, not clearly at rest
- `turn_detection_agent`: it is our turn
- `community_cards_agent`: no community cards are face-up
- `showdown_outcome_agent`: not in showdown
- `held_card_recognition_agent`: face-down card near the lower-right seat area is unreadable
- `blind_button_recognition_agent`: dealer button visible but seat unclear; big blind at seat 5
- `bet_recognition_agent`: chips present in both betting areas, but counts are partially occluded and unreliable
- `chip_recognition_agent`: inventory counts are approximate and partially occluded

## Decision

`wait`

Reason: the table is still changing and the robot is not settled enough for a safe next-step decision.
