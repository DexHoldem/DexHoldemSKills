# Visual Evidence

Source image:
- `s36/00_capture.jpg`

Subagent evidence:
- `scene_stability_agent`: scene appears visually settled; cards, chips, buttons, and the robot hand are sharp with no motion blur. Temporal stability could not be fully verified without a prior frame.
- `turn_detection_agent`: it is our turn; the small white turn button is visible near the lower-left edge of the table and reads `Your Turn`.
- `community_cards_agent`: visible community cards are `Qs`, `Qh`, likely `7d`/`7h` partly blocked by the robot hand, `Qc`, and one additional card that is unreadable or mostly occluded.
- `bet_recognition_agent`: robot/player bet area shows `0 red, 2 blue, 1 green, 2 brown` visible; opponent bet area shows approximately `2 red, 5 blue, 0 green, 0 brown` visible, with some uncertainty due to occlusion.
- `blind_button_recognition_agent`: dealer button is on the opponent side, small blind is on the opponent side, and big blind is on the robot side.

Notes:
- No robot actions were executed.
- Main-agent image perception was not used; this file merges subagent evidence only.
