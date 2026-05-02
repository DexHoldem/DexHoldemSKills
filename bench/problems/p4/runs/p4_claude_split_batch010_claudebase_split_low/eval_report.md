# Eval Report — p4_claude_split_batch010_claudebase_split_low

**State:** s2  
**Image:** s2/00_capture.jpg  
**Run date:** 2026-05-02  

---

## Visual Agents (run in parallel, 9 total)

| Agent | Key Finding |
|---|---|
| scene-stability-agent | `scene_stable: true` — arm retracted to near-edge; no motion blur |
| turn-detection-agent | `is_my_turn: true` — "Your Turn" button visible at robot seat |
| robot-behavior-agent | `action_progress: moving` — hand near hole-card zone, pick_card in progress, safety_ok |
| community-cards-agent | `community_cards: []` — all five slots face-down |
| chip-recognition-agent | my_chips: {5:4, 10:6, 50:2, 100:2}; opponent_chips: {5:3, 10:5, 50:2, 100:2} |
| bet-recognition-agent | my_bet: {5:2, 10:2, 100:1}; opponent_bet: {5:1, 10:8} |
| blind-button-recognition-agent | dealer=opponent, small_blind=opponent, big_blind=robot |
| showdown-outcome-agent | `showdown_visible: false`, outcome: none |
| held-card-recognition-agent | `card_visible: false` — pick_card still executing; no readable card |

All 9 agents ran concurrently (single wave). No reasoning agent invoked (loop_stage=acting, no choose_poker_action requested).

---

## Parsed State Written

**File:** s2/01_parsed_state.md  
- loop_stage: `acting`
- scene_stable: `true`
- is_my_turn: `true`
- community_cards: `[]`
- held card: not yet visible (pick_card dispatched)
- showdown: none

---

## Router Decision (manual trace — executor not run)

**Route:** `wait`  
**Reason:** loop_stage=acting + scene_stable=true → router always waits to let the robot action settle.  
**Suggested action:** `{"action": "wait", "reason": "robot_acting", "sleep_seconds": 3}`  
**Safety counters:** consecutive_waits 1→2 (limit: 20), total_waits 1→2 (limit: 200). Well within bounds.  
**Agent required:** No  
**Robot actions executed:** None (per task instructions)

---

## Output Files

| File | Status |
|---|---|
| runs/p4_claude_split_batch010_claudebase_split_low/visual_raw/scene-stability-agent.md | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/visual_raw/turn-detection-agent.md | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/visual_raw/robot-behavior-agent.md | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/visual_raw/community-cards-agent.md | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/visual_raw/chip-recognition-agent.md | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/visual_raw/bet-recognition-agent.md | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/visual_raw/blind-button-recognition-agent.md | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/visual_raw/showdown-outcome-agent.md | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/visual_raw/held-card-recognition-agent.md | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/visual_summary.json | ✓ written |
| runs/p4_claude_split_batch010_claudebase_split_low/eval_report.md | ✓ written |
| s2/01_parsed_state.md | ✓ written |
