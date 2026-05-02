# DexHoldem Perception Step

## State
- `s24`
- Loop stage: `acting`
- Turn: `true`
- Blind: `big_blind`

## Visual Merge
- Community cards: `7d`, `6s`, and one uncertain card position
- Robot-held hole cards: `7d`, `6s`
- My current bet: `1 x 10`
- Opponent bet: `1 x 50`
- Dealer: `opponent`
- Small blind: `opponent`
- Big blind: `robot`

## Inventory
- My chips: `4 x 5`, `3 x 10`, about `3 x 50`, about `2 x 100`
- Opponent chips: `4 x 5`, `4 x 10`, about `3 x 50`, about `3 x 100`

## Stability
- `scene_stable`: unresolved from the dedicated stability subagent, so kept `false` in the summary to avoid over-claiming scene readiness.

## Notes
- No robot action was executed.
- The main agent did not perform image perception directly; the summary was merged from visible subagent evidence only.
