# Eval Report

## Result
Perception step completed for `choose_poker_action`.

## Evidence Used
- `visual_raw/turn_detection_agent.md`
- `visual_raw/community_cards_agent.md`
- `visual_raw/blind_button_recognition_agent.md`
- `visual_raw/chip_recognition_agent.md`
- `visual_raw/held_card_recognition_agent.md`
- `visual_raw/scene_stability_agent.md`
- `visual_raw/reasoning_agent.md`

## Merged Findings
- It is our turn.
- No face-up community cards are visible.
- Dealer is on the opponent, small blind is opponent, big blind is robot.
- No readable robot-held hole card is visible.
- Scene stability is questionable because the robot gripper still occludes part of the table.

## Reasoning
The reasoning subagent was blocked by the environment's `inherit` model limitation, so a fallback reasoning subagent was used with the parsed state only. It recommended `{"action":"check"}` because there is no outstanding bet in the parsed state and no community cards are visible.

## Verification
- Requested output directory exists.
- `visual_raw/` contains real evidence files.
- `visual_summary.json` exists.
- `eval_report.md` exists.
