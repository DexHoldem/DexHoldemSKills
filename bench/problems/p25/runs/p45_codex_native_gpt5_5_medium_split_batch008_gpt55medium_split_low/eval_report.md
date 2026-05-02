# Eval Report

Perception step completed for `s42`.

## Merged Evidence

- Scene stability: stable enough to continue.
- Turn state: it is our turn.
- Blind/dealer assignment: dealer opponent, small blind opponent, big blind robot.
- Community cards: `Qs`, `Qh`, `7d`, `6s`, `Ac`.
- Bet evidence:
  - Robot/player area shows `10x1`, `50x1`, `100x3`, `5x0`.
  - Opponent area shows `5x2`, `10x5`, `50x1`, `100x0` with partial occlusion uncertainty.

## Decision

No robot action was executed. The task requested perception only, so the run output records the visual state without committing a poker action.

## Evidence Files

- `visual_raw/community_cards_agent.md`
- `visual_raw/blind_button_recognition_agent.md`
- `visual_raw/turn_detection_agent.md`
- `visual_raw/bet_recognition_agent.md`
- `visual_raw/scene_stability_agent.md`
