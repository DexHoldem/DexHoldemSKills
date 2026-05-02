# DexHoldem Perception Step

Current state: `s23`

## Merged Judgments

- Scene is stable enough for perception.
- It is our turn.
- Community cards are not readable; all five visible positions appear face-down.
- Dealer is on the opponent side, with opponent as small blind and robot as big blind.
- My current bet is one blue chip worth 10.
- Opponent bet is partially occluded; best read is one blue 10-chip and two brown 100-chips, but confidence is low.
- Visible chip inventory was estimated for both sides, with the right-side counts less reliable due to occlusion.
- Robot-held hole cards are not safely readable.
- Robot hand is still in progress near chips, but no clear safety issue was identified.
- This is not showdown.

## Action

- No robot action was executed.
- No Texas Hold'em reasoning subagent was needed because this was a perception-only step and no router action was being committed.

## Notes

- All evidence was sourced from scoped visual subagents only.
- The main agent did not perform image perception directly.
