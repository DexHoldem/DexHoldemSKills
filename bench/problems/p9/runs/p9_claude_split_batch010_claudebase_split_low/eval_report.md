# DexHoldem Perception Eval Report

**Run ID:** p9_claude_split_batch010_claudebase_split_low  
**State:** s7  
**Image:** s7/00_capture.jpg  
**Date:** 2026-05-02  

---

## Router Decision

| Field | Value |
|-------|-------|
| Route | `wait` |
| Reason | Scene is unstable; wait and preserve the current sequence |
| Agent required | No |
| Suggested action | `{"action": "wait", "reason": "scene_unstable", "sleep_seconds": 3}` |

---

## Visual Parse: s7

**Loop stage:** `acting`  
**Action sequence context:** `view_left_hole_card`, current step `put_down_card` (dispatched)

### Table State

| Field | Value | Uncertain |
|-------|-------|-----------|
| scene_stable | false | No |
| is_my_turn | true | No |
| community_cards | [] | No |
| my_chips | {5:4, 10:5, 50:2, 100:2} | Yes |
| opponent_chips | {5:3, 10:4, 50:2, 100:2} | Yes |
| my_current_bet | {5:2, 10:3, 50:0, 100:0} | Yes |
| opponent_bet | {5:3, 10:4, 50:0, 100:0} | Yes |

### Robot Behavior

Hand is near the hole-card zone with no card visibly held. Fingers not mid-motion; arm not blurred. The put_down_card action appears mechanically complete (left hole card 9d returned face-down). However the arm is still extended and not yet retracted to an idle pose, triggering the scene-unstable determination.

---

## Agent Evidence Summary

### scene-stability-agent
- **Result:** `scene_stable = false`
- Arm still extended/forward after put_down_card; compared s6 (card in grip) vs s7 (card released but arm not retracted). Not suitable for atom_idle transition yet.

### robot-behavior-agent
- **Result:** Put_down_card action physically complete; no card in hand; hand settled near hole-card zone; no recovery needed.
- No disturbed objects; hole-card slots contain face-down cards as expected.

### turn-detection-agent
- **Result:** `is_my_turn = true`
- White "Your Turn" button visible at bottom-left (robot seat area), clearly readable.

### community-cards-agent
- **Result:** `community_cards = []`
- All 5 community card slots show face-down gray placeholders. Pre-flop.

### chip-recognition-agent
- **Result:** Robot ~{5:4, 10:5, 50:2, 100:2}; Opponent ~{5:3, 10:4, 50:2, 100:2}
- Counts uncertain due to robot arm occluding part of inventory and perspective angle on opponent chips.

### bet-recognition-agent
- **Result:** My bet ~{5:2, 10:3}; Opponent bet ~{5:3, 10:4}
- Chip overlap and camera angle make exact counts uncertain. Consistent with pre-flop blinds posted.

---

## Router Judgment Trace

| Check | Result | Reason |
|-------|--------|--------|
| capture_exists | true | 00_capture.jpg exists |
| parsed_state_exists | true | 01_parsed_state.md exists |
| parsed_state_valid | true | parsed state JSON has a table object |
| action_sequence_valid | true | action_sequence.json loaded |
| hole_card_cache_valid | true | hole_card_cache.json loaded |
| loop_stage_source | parsed_state | loop_stage read from parsed state |
| loop_stage_valid | true | loop_stage is acting |
| table_required_fields | true | table has fields required for loop_stage acting |
| scene_stable | false | parsed state marks the scene unstable → WAIT |

**Safety counters:** consecutive_waits=1 (limit: not exceeded), total_waits=1 (limit: not exceeded). Wait issued safely.

---

## Hole Card Cache

| Slot | Card | Status |
|------|------|--------|
| left | 9d | recognized (source: s5) |
| right | null | unknown |

Left card (9d) was read in s5 and put_down_card was dispatched in s7. Right card still unknown — will be viewed after this sequence completes.

---

## Next Steps (not executed)

1. Execute wait (3s) → recapture
2. Re-parse next state to check if arm has retracted (expect `scene_stable=true`, `loop_stage=atom_idle`)
3. Verify put_down_card dispatched step result → complete step
4. Proceed to view right hole card
