# Eval Report

## Result
Perception could not be completed from the available capture evidence.

## What Was Done
- Ran the visible split visual subagents in parallel where possible.
- Collected returned evidence only; no main-agent image perception was performed.
- Did not execute any robot actions.

## Outcome
- `scene_stable`: unknown
- `is_my_turn`: unknown
- `community_cards`: unknown
- `my_chips`: unknown
- `opponent_chips`: unknown
- `my_current_bet`: approximate, but not fully reliable
- `opponent_bet`: approximate, but not fully reliable
- `dealer_button` / blinds: unknown
- `held_card`: unknown
- `robot_behavior`: unknown
- `showdown_outcome`: unknown

## Limitation
The subagents repeatedly reported the referenced capture path as missing or unreadable, so there was not enough visual evidence to produce a reliable perception result.
