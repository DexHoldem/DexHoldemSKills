# DexHoldem Perception Report

State: `s41`

## Summary
- Scene stability: unstable
- Turn: our turn
- Community cards: `9c`, `4h`
- Hole cards: unreadable
- Showdown: not showdown
- Blind/button: dealer on opponent side, small blind opponent, big blind robot
- Robot behavior: action appears in progress, not settled

## Evidence Notes
- The turn-detection subagent identified the visible `Your Turn` marker on the robot side.
- The scene-stability subagent judged the frame unstable because the robot arm is extended across the table and the capture is still occluded.
- The community-card subagent saw two cards on the board row: `9c` and `4h`.
- The held-card subagent could not read either robot-held hole card.
- The showdown subagent found no showdown evidence.

## Parsed Table
- `scene_stable`: false
- `is_my_turn`: true
- `community_cards`: `9c`, `4h`
- `my_chips`: 4 red 5-chips, 3 blue 10-chips, 0 green 50-chips, 0 brown 100-chips
- `opponent_chips`: partially occluded; at least 2 blue 10-chips visible
- `my_current_bet`: unknown
- `opponent_bet`: unknown
- `dealer_button`: opponent
- `small_blind`: opponent
- `big_blind`: robot

## Output Notes
- No robot action was executed.
- Perception evidence was merged from the visible subagents only.
