# Eval Report

## Outcome

Perception step completed from subagent evidence only. The scene is not stable enough to continue into a robot action.

## Evidence

- `scene_stability_agent`: unstable. The robot arm/camera shifted between the last two captures, so the frame is still settling.
- `turn_detection_agent`: it is our turn. The white physical turn button is visible near the lower-left robot seat.
- `community_cards_agent`: five community cards are visible: `10s, 8h, 7d, 6s, 7c`.
- `blind_button_recognition_agent`: dealer and small blind are on the opponent side; big blind is on the robot side.
- `chip_recognition_agent`: robot inventory is estimated at red 4, blue 3, green 0, brown 0; opponent inventory is estimated at red 2, blue 3, green 1, brown 2.
- `robot_behavior_agent`: the robot hand is still hovering/reaching over the betting area and does not look settled.
- `held_card_recognition_agent`: no readable robot-held hole card is visible in the capture.
- `showdown_outcome_agent`: the table appears at or near showdown, but there is no explicit winner/loser cue.

## Interpretation

The board is fully run out and the turn button says it is our turn, but the stability evidence dominates: the robot hardware is still moving or settling. That means the safe perception result is `unstable`, not a transition into any action.

## Action

No robot action was executed.

## Output Files

- `runs/p47_codex_split_batch007_codexbase_split_low/visual_raw/`
- `runs/p47_codex_split_batch007_codexbase_split_low/visual_summary.json`
- `runs/p47_codex_split_batch007_codexbase_split_low/eval_report.md`
