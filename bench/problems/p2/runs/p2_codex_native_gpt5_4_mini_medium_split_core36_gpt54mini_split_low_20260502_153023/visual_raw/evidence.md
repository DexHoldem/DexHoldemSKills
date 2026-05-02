# Visual Evidence

- `scene_stability_agent`: Compared only `s0/00_capture.jpg`; no earlier capture existed in this run. Reported the scene as unstable/uncertain because frame-to-frame settling could not be verified. Noted the table, seated human, and robot hand on the right side.
- `turn_detection_agent`: Reported `No`; the physical turn marker is on the upper/opponent side, not the robot side.
- `blind_button_recognition_agent`: Reported robot `big_blind`. Evidence: a yellow `BIG BLIND` button is visible on the bottom/robot side, and a white dealer button is visible on the top/opponent side.
- `community_cards_agent`: Reported five visible board positions, all face-down/unreadable gray backs with diagonal striping. No ranks or suits were readable.
- `robot_behavior_agent`: Only workflow-level evidence was returned. With `loop_stage=idle`, `current_step=null`, and `steps=[]`, it indicated no active robot action and no visible safety concern, but also said it could not inspect pose directly without a previous image.
- `chip_recognition_agent`: Returned robot inventory estimate `4/7/1/3` for `5/10/50/100` and opponent inventory estimate `2/4/3/4`, with partial occlusion on the right-side clusters.
- `bet_recognition_agent`: Returned robot bet estimate `4/7/1/2` and opponent bet estimate `4/5/1/0`, with the right-side robot cluster and some opponent area partly occluded.

