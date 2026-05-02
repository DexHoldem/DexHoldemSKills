# Visual Evidence

- `scene_stability_agent`: Compared `s_current/00_capture.jpg` with `s0/00_capture.jpg`; scene is stable with no visible motion or object displacement.
- `turn_detection_agent`: `No`; the small white turn button is closer to the player across the table, so it is not our turn.
- `blind_button_recognition_agent`: `big_blind`; yellow `BIG BLIND` button visible at seat 5.
- `community_cards_agent`: `4c`, `Ac`, `Jh` with `Jh` least certain.
- `robot_behavior_agent`: hand extended from right side over upper-middle/opponent-side betting lane; not holding a card or chips; not near rest pose; scene safe and settled.
- `chip_recognition_agent` pass 1: robot `{5:1, 10:2, 50:1, 100:2}`; opponent `{5:2, 10:2, 50:0, 100:1}`; opponent top-center/right clusters ambiguous and some chips near the dealer/button area excluded as possible current bets.
- `chip_recognition_agent` pass 2: robot `{5:1, 10:1, 50:1, 100:1}`; opponent `{5:2, 10:2, 50:2, 100:3}`; opponent top-left chips partially ambiguous with inventory stacks.
- Merged inventory estimate favors the conservative pass-2 read for robot and the higher opponent stack count from pass 2, with ambiguity remaining in the opponent clusters.
- `bet_recognition_agent`: robot current bet area best visible count `5:3, 10:3, 50:1, 100:2`; opponent current bet area best visible count `5:3, 10:4, 50:3, 100:3`; some right-side/opponent chips partially occluded by the camera arm.
- Durable context from `action_sequence.json` and `hole_card_cache.json`: loop stage `idle`, waiting for opponent; cached board note says `heart J, club A, club 4`; cached bets note says my bet `10:1, 100:1`, opponent bet `5:2, 100:1`.
