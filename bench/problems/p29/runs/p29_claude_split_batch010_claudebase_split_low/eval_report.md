# Eval Report — p29_claude_split_batch010_claudebase_split_low

## Run Summary

- **Run ID:** p29_claude_split_batch010_claudebase_split_low
- **State:** s25
- **Visual setting:** split (9 visual subagents + 1 reasoning agent)
- **Capture:** s25/00_capture.jpg

## Visual Subagent Results

| Agent | Key Finding |
|---|---|
| scene-stability-agent | scene_stable=true (post-action pose, no in-transit objects) |
| turn-detection-agent | is_my_turn=true ("Your Turn" button visible) |
| community-cards-agent | ["4c","6c","6s","6d","4s"] — river (5 cards) |
| held-card-recognition-agent | ["9d","5d"] — from cache (no visible held card in frame) |
| blind-button-recognition-agent | dealer=opponent, small_blind=opponent, big_blind=robot |
| chip-recognition-agent | my_chips=300, opponent_chips=500 |
| bet-recognition-agent | my_current_bet=20, opponent_bet=205 (uncertain — arm occlusion) |
| robot-behavior-agent | action_in_progress=false, is_safe=true |
| showdown-outcome-agent | showdown_active=false |

## Poker Reasoning

**Board:** 4c 6c 6s 6d 4s — sixes full of fours (river complete)  
**Hole cards:** 9d 5d  
**Hand strength:** Plays the board (sixes full of fours) — no outright win possible

**Situation:** Opponent has raised ~185 chips to call on the river. With no possibility of winning outright (only chop at best, lose at worst if opponent holds a 6 for quads), calling is -EV.

**Reasoning agent recommendation:** `fold`  
**Validation:** Confirmed correct. 9d 5d cannot beat the board. The only way to win is if the opponent also plays the board (chop), but given the large river bet, opponent likely holds a 6 for four-of-a-kind. Folding is the correct decision.

## Router Decision

- Route: `visual_parse` (01_parsed_state.md written for s25)
- Next expected route: `choose_poker_action` → action written to s25/02_action.md
- **Robot action NOT executed** (per task instructions)

## Output Files

- `visual_raw/` — 9 agent evidence files written
- `visual_summary.json` — merged table state and recommended action
- `eval_report.md` — this file

## Uncertainties

- `opponent_bet`: robot arm occludes upper-right table; estimated 205 but range 100–250 plausible
- Community cards positions 1 and 5 (4c, 4s): moderate uncertainty in pip/suit reading due to camera angle
- Chip counts are approximate due to overlap and camera angle
