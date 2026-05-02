## Visual Evidence Summary

- `scene_stability_agent`: `s32/00_capture.jpg` compared against `s31/00_capture.jpg` is unstable because new face-down cards appear in the upper middle area of `s32/00_capture.jpg` that are not present in `s31/00_capture.jpg`.
- `robot_behavior_agent`: the robot arm is extended from the right, not near rest, with no held object visible; `collect_winnings` appears still in progress and safe/retryable.
- `turn_detection_agent`: the physical turn marker reads `Your Turn`, so it is our turn.
- `blind_button_recognition_agent`: opponent is big blind, robot is dealer and small blind by visible `BIG BLIND` button and two-player rules.
- `community_cards_agent`: left to right board evidence is unreadable/face-down, `8h`, `7d`, `6s`, `7c`.
- `bet_recognition_agent`: robot current bet area `5:3, 10:3, 50:0, 100:1`; opponent current bet area `5:2, 10:2, 50:0, 100:0`.
- `chip_recognition_agent`: robot inventory `5:4, 10:3, 50:4, 100:2`; opponent inventory `5:2, 10:5, 50:0, 100:0`, with some occlusion uncertainty.
- `showdown_outcome_agent`: recommended outcome is `not_showdown`; opponent hole cards are not face-up and robot hole cards remain cached as `9d` and `5d`.
