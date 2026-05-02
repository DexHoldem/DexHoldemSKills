# Eval Report

Current perception step for `s28` is recorded from split visual evidence only.

## Evidence
- `blind_button_recognition_agent`: dealer `robot`, small blind `robot`, big blind `opponent`
- `turn_detection_agent`: it is our turn
- `scene_stability_agent`: unstable, camera/table state shifted between `s27` and `s28`
- `community_cards_agent`: 4 visible community cards read as `8h`, `7d`, `6s`, `7c` with one unreadable leftmost position
- `held_card_recognition_agent`: robot hand does not show a readable card
- `bet_recognition_agent`: robot bet area shows `2 blue`, `1 green`, `3 brown`; opponent bet area shows `2 red`, about `4 blue`, with some occlusion
- `chip_recognition_agent`: no completed response
- `showdown_outcome_agent`: showdown not visible; no clear win/lose decision

## Assessment
The scene is not stable enough to treat as a settled decision point. Visual evidence suggests the turn button is present and it is our turn, but the scene instability means the step should be treated cautiously.

No robot action was executed.
