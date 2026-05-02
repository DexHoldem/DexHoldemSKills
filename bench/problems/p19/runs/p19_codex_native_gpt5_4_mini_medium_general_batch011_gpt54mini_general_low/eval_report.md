# Eval Report

Perception-only run completed for `s18`.

## Outcome

- `scene_stable`: yes
- `is_my_turn`: yes
- `community_cards`: not reliably readable from the merged evidence
- `my_chips`: not extracted
- `opponent_chips`: not extracted
- `my_current_bet`: not extracted
- `opponent_bet`: not extracted
- Visible turn indicator: `Your Turn`
- Visible blind indicator: `BIG BLIND`

## Evidence

- Raw evidence file: [`visual_raw/visual_agent.md`](./visual_raw/visual_agent.md)

## Notes

- The main agent did not inspect the image directly.
- I used visual subagent evidence only for the perception summary.
- The reasoning subagent could not be used here because the visible reasoning agent inherited an unsupported model on this account, so no poker action was committed.
