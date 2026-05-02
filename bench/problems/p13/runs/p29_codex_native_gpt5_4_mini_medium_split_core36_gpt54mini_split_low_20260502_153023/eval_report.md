# Visual Perception Report

- Scene is not stable compared with `s24/00_capture.jpg` and `s25/00_capture.jpg`.
- The turn marker indicates it is our turn.
- Blind assignment: robot is `small_blind`; the visible `BIG BLIND` marker is on the other seat.
- Community board evidence shows `7d`, `6s`, `7c`, with the earlier board positions unreadable/occluded in this frame.
- Estimated chip inventories:
  - My chips: `5: 4`, `10: 3`, `50: 2`, `100: 3`
  - Opponent chips: `5: 4`, `10: 5`, `50: 3`, `100: 3`
- Estimated current bets:
  - My bet: `5: 0`, `10: 1`, `50: 0`, `100: 1`
  - Opponent bet: `5: 2`, `10: 2`, `50: 1`, `100: 2`
- Workflow merge: `loop_stage` best fits `atom_idle` because the scene is settled enough for counting, but the action sequence is still pending.

## Raw Evidence

- `scene_stability_agent`: compared `s24/00_capture.jpg` and `s25/00_capture.jpg`; reported the scene as unstable.
- `turn_detection_agent`: reported `Your Turn`.
- `blind_button_recognition_agent`: reported the `BIG BLIND` marker on seat 5 and inferred the other seat as button/small blind.
- `community_cards_agent`: reported `7d`, `6s`, `7c`, with the first two positions unreadable/occluded.
- `chip_recognition_agent`: estimated inventory counts for both players.
- `bet_recognition_agent`: estimated current-bet chip counts.
