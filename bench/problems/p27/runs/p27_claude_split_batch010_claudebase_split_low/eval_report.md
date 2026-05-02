# Eval Report — p27_claude_split_batch010_claudebase_split_low

**Problem:** p27  
**State processed:** s22  
**Capture:** s22/00_capture.jpg  

## Visual Subagents (run in parallel, single wave)

| Agent | Result | Confidence |
|---|---|---|
| scene-stability-agent | scene_stable=**true** | 0.78 |
| turn-detection-agent | is_my_turn=**null** (button not visible) | 0.20 |
| community-cards-agent | community_cards=**[]** (preflop) | 0.88 |
| chip-recognition-agent | my={5:3,10:2,50:1,100:0}; opp={5:2,10:3,50:2,100:3} | 0.35 |
| bet-recognition-agent | my_bet={5:2,10:1}; opp_bet={50:1,100:2} | 0.45 |
| blind-button-recognition-agent | dealer=opponent, SB=opponent, BB=robot | 0.88 |
| robot-behavior-agent | hand extended, not gripping, safety_ok=true | 0.72 |

## Evidence Merge

- **scene_stable**: true (high confidence, scene clear after arm retraction)
- **is_my_turn**: merged as **false** — visual confidence was low (0.20, button not visible), but prior state s21 and action_sequence.json both confirm opponent's turn ("wait_for_opponent")
- **community_cards**: [] — preflop, all board positions face-down (high confidence)
- **blinds**: dealer=opponent, SB=opponent, BB=robot (matches hole_card_cache.json)
- **my_chips / opponent_chips**: low confidence (0.35) due to arm occlusion; marked as uncertain_fields
- **my_current_bet / opponent_bet**: moderate confidence (0.45); marked uncertain due to partial occlusion

## Router Decision

Path through router.py:
1. capture_exists ✓
2. parsed_state_exists ✓ (written this step)
3. no 02_action.md yet
4. parsed_state_valid ✓
5. action_sequence_valid ✓, hole_card_cache_valid ✓
6. loop_stage=idle (from parsed_state)
7. all idle-stage required fields present ✓
8. scene_stable=true ✓
9. is_my_turn=false → **route: wait**

**Action:** `{"action": "wait", "reason": "not_my_turn", "sleep_seconds": 3}`

## Reasoning Agent

Not invoked — poker action selection was not reached (is_my_turn=false routes to wait before hole card and action selection logic).

## Output Files

- `s22/01_parsed_state.md` — written
- `s22/02_action.md` — written
- `runs/p27_claude_split_batch010_claudebase_split_low/visual_raw/` — 7 evidence files
- `runs/p27_claude_split_batch010_claudebase_split_low/visual_summary.json` — written
- `runs/p27_claude_split_batch010_claudebase_split_low/eval_report.md` — this file
