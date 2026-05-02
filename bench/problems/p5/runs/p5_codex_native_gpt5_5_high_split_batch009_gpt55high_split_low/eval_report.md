# Eval Report

Current perception step completed for run `p5_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low`.

## Outcome

- Scene stability: unstable.
- Turn detection: it is our turn.
- Community cards: five visible, but all are face down and unreadable.
- Held card: a face-down card appears to be held or touched, but it is unreadable.

## Interpretation

The latest available completed frame pair indicates the robot is still mid-action, so the scene is not settled enough for a new robot action or poker decision. Even though the turn button indicates it is our turn, the active robot motion dominates the step outcome.

## Result

- Recommended next state: wait and recapture.
- No robot action executed.

## Evidence

- [`scene_stability_agent.md`](runs/p5_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_raw/scene_stability_agent.md)
- [`turn_detection_agent.md`](runs/p5_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_raw/turn_detection_agent.md)
- [`community_cards_agent.md`](runs/p5_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_raw/community_cards_agent.md)
- [`held_card_recognition_agent.md`](runs/p5_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low/visual_raw/held_card_recognition_agent.md)
