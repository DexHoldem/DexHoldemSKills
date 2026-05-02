# Perception Report

## Outcome

The current DexHoldem perception step is complete for `s48`.

## Merged Evidence

- Scene stability: stable.
- Turn detection: it is our turn.
- Community cards: `Ts 8d 7d 6s 7c`.
- Bet recognition:
  - Bottom side bet: 5 red, 3 blue, 1 green, with some uncertainty on the right side.
  - Top side bet: 2 red, 4 blue, with a possible extra hidden chip near the right edge.
- Inventory counts:
  - Top/opponent inventory: about 2 red, 5 blue, 3 green, 2 brown, with some occlusion uncertainty.
  - Bottom/robot inventory: about 4 red, 5 blue, 1 green, 3 brown, with some occlusion uncertainty.

## Router-Relevant Note

This state is `atom_idle`, so the visible reasoning subagent was not required. The router did not request `choose_poker_action`; therefore no poker-action reasoning was committed.

## Files Written

- `runs/p49_codex_split_batch007_codexbase_split_low/visual_raw/scene_stability_agent.md`
- `runs/p49_codex_split_batch007_codexbase_split_low/visual_raw/turn_detection_agent.md`
- `runs/p49_codex_split_batch007_codexbase_split_low/visual_raw/community_cards_agent.md`
- `runs/p49_codex_split_batch007_codexbase_split_low/visual_raw/bet_recognition_agent.md`
- `runs/p49_codex_split_batch007_codexbase_split_low/visual_raw/chip_recognition_agent.md`
- `runs/p49_codex_split_batch007_codexbase_split_low/visual_summary.json`
- `runs/p49_codex_split_batch007_codexbase_split_low/eval_report.md`
