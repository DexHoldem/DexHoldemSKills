# Eval Report

Current state: `s21`

Summary:
- The scene is stable.
- It is our turn.
- No community cards are readable in this capture.
- Held cards are unreadable from this image.
- Blind/dealer assignment is unclear.
- The robot arm is extended and the action appears to still be in progress.
- No showdown evidence is present.

Evidence merge:
- `turn_detection_agent`: white `Your Turn` button visible near the lower-left table area.
- `community_cards_agent`: no readable board cards.
- `blind_button_recognition_agent`: no distinct blind button visible.
- `bet_recognition_agent`: robot-side bet cluster partially visible, about 5 red 5-chips and 1 blue 10-chip, but occluded.
- `held_card_recognition_agent`: no readable hole card.
- `robot_behavior_agent`: arm extended, action in progress, physically safe.
- `scene_stability_agent`: stable single-frame capture.
- `showdown_outcome_agent`: not showdown.
- `chip_recognition_agent`: robot inventory partially visible, about 4 red 5-chips and 1 blue 10-chip.

Routing note:
- No Texas Hold'em action reasoning was needed for this perception step because the output is a perception summary, not a committed robot action.

