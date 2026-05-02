# Eval Report

## Result

Perception step completed for `s28` and merged into `visual_summary.json`.

## Evidence

- `turn_detection_agent` reported it is our turn with high confidence.
- `scene_stability_agent` reported the scene is stable, with medium confidence.
- `community_cards_agent` read four community cards: `Qh`, `7d`, `6s`, `7c`.
- `chip_recognition_agent` counted remaining inventory chips for both sides.
- `bet_recognition_agent` counted the current bet chips on both sides.
- `blind_button_recognition_agent` identified dealer/small blind as opponent and big blind as robot.
- `held_card_recognition_agent` reported both hole cards as unreadable face-down cards.
- `robot_behavior_agent` reported the robot is still moving / action in progress.
- `showdown_outcome_agent` found no clear showdown.

## Interpretation

The merged parse indicates a stable enough table read for perception, but the robot is still in motion, so I did not commit any poker action or robot command.

## Files Written

- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/scene_stability_agent.md`
- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/turn_detection_agent.md`
- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/community_cards_agent.md`
- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/chip_recognition_agent.md`
- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/bet_recognition_agent.md`
- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/blind_button_recognition_agent.md`
- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/held_card_recognition_agent.md`
- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/robot_behavior_agent.md`
- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/showdown_outcome_agent.md`
- `runs/p30_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_summary.json`
