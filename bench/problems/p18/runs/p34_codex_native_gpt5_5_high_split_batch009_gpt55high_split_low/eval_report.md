# DexHoldem Perception Report

Current step: `choose_poker_action`

## Merged Evidence

- Scene is stable.
- It is our turn.
- Community cards read as `Qh`, `7d`, `Qs`, `3c`.
- Robot-held card is unreadable from this frame.
- Dealer and small blind are on the opponent side; big blind is on the robot side.
- Current bet area on the robot side shows `2` blue `10`-chips, `2` green `50`-chips, and `2` brown `100`-chips.
- Opponent bet area is occluded and not countable.

## Reasoning Status

The visible reasoning subagent could not be used successfully in this environment
because the backend rejected the inherited model configuration. No poker action
was committed.

## Output Verification

- `visual_raw/` contains real evidence files.
- `visual_summary.json` written.
- `eval_report.md` written.
