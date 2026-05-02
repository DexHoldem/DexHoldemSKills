# DexHoldem Perception Report

- Run directory: `runs/p6_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low`
- Source capture: `s_current/00_capture.jpg`
- Current state: `s4`
- Loop stage: `acting`

## Merged Visual Judgment

- Scene is stable.
- It is the robot/player turn.
- The robot hand is holding a hole card.
- The card face is not readable from the capture.
- No obvious robot recovery is needed from this frame.

## Table State

```json
{
  "scene_stable": true,
  "is_my_turn": true,
  "community_cards": [],
  "my_chips": {"5": 4, "10": 4, "50": 4, "100": 4},
  "opponent_chips": {"5": 4, "10": 4, "50": 4, "100": 4},
  "my_current_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
  "opponent_bet": {"5": 0, "10": 0, "50": 0, "100": 0}
}
```

## Evidence

- Scene stability agent: stable, no visible motion blur.
- Robot behavior agent: hand is stable, near rest, and not obviously in a failed state.
- Held-card agent: hole card is present but unreadable.
- Turn detection agent: "Your Turn" button is visible.

## Constraints

- No robot actions were executed.
- Main-agent image perception was not used; this report merges subagent evidence only.
