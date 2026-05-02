# Visual Evidence

- `scene_stability_agent`: stable; compared `s0/00_capture.jpg` with no previous state image available; scene looks settled, but stability is inferred from a single capture.
- `robot_behavior_agent`: right-side dexterous hand is in the upper-right occlusion zone, hovering over the opponent-side central betting lane; motion appears in progress for `collect_winnings`; not near rest.
- `turn_detection_agent`: it is our turn; the white `Your Turn` button is visible near the bottom-left robot seat area.
- `blind_button_recognition_agent`: dealer/small blind at opponent seat; robot is big blind.
- `community_cards_agent`: five community cards visible, left to right `Kd`, `Ks`, `4c`, `As`, `Jd`; fifth card slightly uncertain.
- `showdown_outcome_agent`: opponent hole cards `3c` and `Js`; robot hole cards `Kc` and `2s`; board `Kd Ks 4c As Jd`; robot wins with three kings over opponent three jacks.
