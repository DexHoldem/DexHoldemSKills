## Raw Visual Evidence

- `s4/00_capture.jpg` -> `s5/00_capture.jpg`: robot arm changes position and is actively holding a card in `s5/00_capture.jpg`.
- `s5/00_capture.jpg`: physical turn marker indicates it is our turn.
- `s5/00_capture.jpg`: scene is not stable enough to continue because the robot hand is still moving with a held card.

## Durable Context Used

- `action_sequence.json`: `loop_stage = atom_idle`, action `view_card` at position `left`.
- `hole_card_cache.json`: left hole card previously recognized as `9d`; right hole card still unknown.
- `s4/01_parsed_state.md`: previous state had no community cards and zero current bets.
