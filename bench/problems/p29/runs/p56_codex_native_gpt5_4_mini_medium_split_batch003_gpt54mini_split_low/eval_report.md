# DexHoldem Perception Step

## Result
The current frame is stable and it is our turn, but the robot hole cards are not readable from the image. The board is complete and the hand appears to be at river/showdown stage, but the visual evidence does not support poker-action selection from the main agent alone.

## Evidence
- `turn_detection_agent`: the white turn button is visible near the bottom-center, so it is our turn.
- `scene_stability_agent`: the scene is stable enough to continue.
- `blind_button_recognition_agent`: dealer is on the robot seat, so robot is small blind and opponent is big blind.
- `community_cards_agent`: five community cards are visible, approximately `Kh`, `3s`, `3c`, `5h`, `Tc`.
- `held_card_recognition_agent`: no readable robot-held hole card is visible.
- `bet_recognition_agent`: current bet chips are visible in both betting areas, with some occlusion.
- `chip_recognition_agent`: chip inventories are approximately readable, but partly occluded.
- `robot_behavior_agent`: robot hand is extended over the table and appears mid-action, but safe.
- `showdown_outcome_agent`: no clear win/lose evidence is visible from this frame alone.

## Router Interpretation
The router would not proceed to `choose_poker_action` from the current visual evidence because the robot hole cards are not readable from the frame. The correct perception outcome is to preserve the stable state and wait for the next step that exposes or caches the hole cards.

## Action
No robot action was executed.
