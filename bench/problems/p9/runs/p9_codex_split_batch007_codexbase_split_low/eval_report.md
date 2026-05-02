# Eval Report

## Outcome

Hold / wait. The current frame is not stable enough to advance the router into a poker action.

## Why

- `scene_stability_agent` marked the scene unstable because the robot hand/object at the bottom right moved between `s6/00_capture.jpg` and `s7/00_capture.jpg`.
- `robot_behavior_agent` said the hand is still reaching over the table and is not in a settled pose.
- `turn_detection_agent` confirmed it is our turn, but turn ownership alone is not sufficient while the scene is still changing.

## Other Evidence

- `community_cards_agent`: 5 community cards are visible, but they are face-down and unreadable.
- `blind_button_recognition_agent`: robot is the big blind; opponent is dealer/small blind, with slight inference uncertainty.
- `chip_recognition_agent`: robot inventory is visible at 5 red / 4 blue / 0 green / 0 brown.
- `bet_recognition_agent`: both current-bet areas contain visible chips, but the exact denominations are partially occluded and not fully reliable.
- `held_card_recognition_agent`: no robot-held hole card is visible.
- `showdown_outcome_agent`: no showdown state or win/lose evidence is visible.

## Decision

No robot action was executed. The correct next step is to wait for the robot hand to settle and then re-evaluate.

