# DexHoldem Perception Eval Report

**Run ID:** p12_claude_split_batch010_claudebase_split_low  
**State:** s7  
**Date:** 2026-05-02  
**Image:** s7/00_capture.jpg

---

## Pipeline Execution

9 visual subagents launched in a single parallel wave. No serialization required; all agents were independent of each other at the visual parse stage. No reasoning subagent was invoked (router resolved to `recover_down` before reaching `choose_poker_action`).

---

## Visual Agent Results

| Agent | Key Finding | Confidence |
|---|---|---|
| scene-stability | scene_stable: **false** — robot arm elevated and moving | 0.90 |
| turn-detection | is_my_turn: **true** — "Your Turn" button visible | 0.97 |
| community-cards | community_cards: **[]** — preflop, no face-up community cards | 0.82 |
| chip-recognition | my_chips: 350, opponent_chips: 445 (uncertain, arm occlusion) | 0.45 |
| bet-recognition | my_current_bet: 20, opponent_bet: 210 (uncertain) | 0.40 |
| blind-button | dealer: opponent, small_blind: opponent, big_blind: robot | 0.85 |
| robot-behavior | arm extended over table, not idle, safety_concern: true, recovery_needed: true | 0.72 |
| showdown-outcome | showdown_active: false, no face-up hole cards | 0.15 |
| held-card | held_card: null (not visually readable; context: 9d target) | 0.35 |

---

## Synthesized Parsed State

- **loop_stage:** `down`
- **scene_stable:** `false`
- **is_my_turn:** `true`
- **street:** preflop
- **community_cards:** []
- **my_chips / opponent_chips:** 350 / 445 (uncertain)
- **my_current_bet / opponent_bet:** 20 / 210 (uncertain)
- **blinds:** opponent=dealer/SB, robot=BB
- **robot status:** arm extended, not idle, safety concern, recovery needed
- **held_card:** null (visual read inconclusive)

---

## Router Decision

**Route:** `recover_down`  
**Agent required:** yes (`recover_down` task)  
**Reason:** `action_sequence.json` has `loop_stage=down` and `human_required=true`. Last error: `put_down_card_failed` — "left hole card put-down requires human help". Robot behavior agent confirms safety concern and recovery needed; scene is unstable.

---

## Action

**No action executed.** Instructions require no robot actions to be taken. The router outcome (`recover_down`) requires human confirmation before any automated retry. The `human_required: true` flag in the action sequence additionally blocks automated recovery.

---

## Files Written

- `s7/01_parsed_state.md` — visual parse output for state s7
- `runs/p12_claude_split_batch010_claudebase_split_low/visual_raw/` — 9 raw evidence files (one per subagent)
- `runs/p12_claude_split_batch010_claudebase_split_low/visual_summary.json` — synthesized perception summary
- `runs/p12_claude_split_batch010_claudebase_split_low/eval_report.md` — this report
