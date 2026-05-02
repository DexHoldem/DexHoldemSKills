# Eval Report

Perception step completed from local setup using visible visual subagents only.

## Result

- Scene stability: unstable
- Turn: it is our turn
- Community cards: Qs, Qh, 7d, 6c, with the fifth board position unreadable

## Evidence

- [scene_stability_agent.md](runs/p37_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/scene_stability_agent.md)
- [robot_behavior_agent.md](runs/p37_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/robot_behavior_agent.md)
- [turn_detection_agent.md](runs/p37_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/turn_detection_agent.md)
- [community_cards_agent.md](runs/p37_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low/visual_raw/community_cards_agent.md)

## Notes

- The robot hand was still in motion over the robot-side card area, so the frame was not treated as settled.
- No robot actions were executed.
- The reasoning subagent was not needed because no choose_poker_action request occurred.
