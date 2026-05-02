# Eval Report

## Outcome
Perception step completed for `s0/00_capture.jpg` using visible subagents only. No robot actions were executed.

## Merged State
- `scene_stable`: `false`
- `is_my_turn`: `false`
- `community_cards`: `4c`, `Ac`, `Jd`
- `my_chips`: `1x5`, `2x10`, `1x50`, `2x100`
- `opponent_chips`: approximately `4x5`, `3x10`, `3x50`, `3x100`
- `my_current_bet`: `0x5`, `1x10`, `0x50`, `1x100`
- `opponent_bet`: approximately `4x5`, `2x10`, `0x50`, `2x100`
- `dealer/small blind`: opponent
- `big blind`: robot

## Evidence Notes
- Turn detection indicated it is not our turn.
- Scene stability was flagged unstable because the hand is still in frame and the right side is occluded.
- Community card recognition returned three visible cards with mild uncertainty on the third card.
- Bet and chip counts were read with occlusion-based uncertainty on the opponent side.

## Routing Implication
No Texas Hold'em action reasoning was required for this step because the visual evidence indicates opponent turn, so the main agent should not commit any poker action.
