# Evaluation Report

Current perception step for `p13_codex_split_batch007_codexbase_split_low`.

## Summary

- The scene is not yet stable enough to continue.
- The white turn button is visible and reads `Your Turn`, so it is our turn from the turn-button evidence.
- The community board is unreadable / face-down, so no shared cards can be confirmed.
- The held card is not readable in the latest capture; a prior parsed state indicates the left hole card was `9d`, but that prior read was not re-derived from the current image.

## Visual Evidence

- `community_cards_agent`: no readable community cards; five face-down backs visible.
- `turn_detection_agent`: `Your Turn` button visible near seat 6.
- `blind_button_recognition_agent`: dealer and small blind unclear; big blind at seat 5.
- `chip_recognition_agent`: robot/player inventory estimated at red 6, blue 5, green 0, brown 0; opponent at red 4, blue 6, green 0, brown 0.
- `held_card_recognition_agent`: held card present but unreadable in the latest capture.
- `robot_behavior_agent`: robot hand extended over the table; action still in progress.
- `scene_stability_agent`: unstable compared with s6 because the robot arm and seated person changed pose.

## Outcome

- Perception evidence was collected and consolidated in the requested output directory.
- No robot action was executed.
- No poker strategy action was committed because the scene remained unstable.
