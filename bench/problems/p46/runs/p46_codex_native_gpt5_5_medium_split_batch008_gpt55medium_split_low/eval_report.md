# DexHoldem Perception Report

Run: `p46_codex_native_gpt5_5_medium_split_batch008_gpt55medium_split_low`
State: `s45`

## Summary

The current frame shows an active showdown. The robot is not holding visible hole cards, the turn indicator says it is our turn, and the robot hand is still extended over the table but appears safe and non-contacting.

## Visual Findings

- Community cards: `Qs`, `Qh`, `7d`, an uncertain black queen card, `7c`
- Turn: our turn
- Buttons: dealer is opponent, small blind is opponent, big blind is robot
- Held cards: no clearly visible robot-held card
- Bets: robot area has `1 blue 10-chip` and `1 green 50-chip`; opponent area has `2 red 5-chips`, `1 blue 10-chip`, and `2 brown 100-chips`
- Inventory: robot and opponent chip inventories were counted with medium confidence because of occlusion in some stacks
- Robot behavior: hand is extended over the table, open/relaxed, no visible unsafe interaction
- Showdown: active, and the showdown agent says the robot loses

## Notes

- The community-card read contains one uncertain suit on the fourth board card, so the board should be treated as partially ambiguous.
- I did not execute any robot actions.
- Raw evidence files were written under `visual_raw/` for every called subagent.
