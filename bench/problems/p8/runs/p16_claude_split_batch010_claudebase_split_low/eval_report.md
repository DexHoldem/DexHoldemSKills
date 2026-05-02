# DexHoldem Perception Eval Report

**Run ID:** p16_claude_split_batch010_claudebase_split_low  
**State:** s15 (s_current)  
**Date:** 2026-05-02

---

## Visual Agents Called (Parallel Wave 1)

| Agent | Result |
|---|---|
| scene-stability-agent | scene_stable: **true** |
| turn-detection-agent | is_my_turn: **true** |
| community-cards-agent | community_cards: **[]**, street: preflop |
| chip-recognition-agent | my_chips: **350**, opponent_chips: **390** (approximate) |
| bet-recognition-agent | my_current_bet: **40**, opponent_bet: **60** (opponent uncertain) |
| blind-button-recognition-agent | dealer: opponent, small_blind: opponent, big_blind: robot |
| robot-behavior-agent | robot_idle: **true**, action_complete: **true** |

All 7 agents ran in a single parallel wave.

---

## Scene Description

The capture (s15/00_capture.jpg) shows the DexHoldem table at preflop. Key observations:

- **Robot hand:** Near idle/rest pose at the right side of the table; arm retracted; not holding a card.
- **Right hole card (5d):** Standing upright in the robot's right hole-card area — consistent with the card having been returned after the `view_card(right)` action.
- **Turn marker:** "Your Turn" (white button) visible at bottom-left — robot's turn.
- **Big Blind button:** Yellow "BIG BLIND" button on robot's side; blue dealer button on opponent's side.
- **Community cards:** All five slots face-down; preflop.
- **Chip stacks:** Both sides have chips scattered in their areas; approximate totals robot=350, opponent=390.
- **Betting area:** Small chips near center — robot bet ~40, opponent bet ~60 (opponent count uncertain due to occlusion by robot arm).

---

## Hole Card Cache

| Slot | Card | Confidence | Source |
|---|---|---|---|
| left | 9d | 1.0 | s5 |
| right | 5d | 1.0 | s15 |

Both hole cards are fully cached.

---

## Router Analysis

After writing `s_current/01_parsed_state.md`, the router would decide:

1. `capture_exists`: ✓
2. `parsed_state_exists`: ✓ (written this step)
3. `02_action.md`: absent → continue
4. `parsed_state_valid`: ✓ (table object with required fields)
5. `loop_stage`: `atom_idle` (from parsed_state)
6. `scene_stable`: true ✓
7. **Enters atom_idle branch**
   - `current_step`: `continue_cached_action_sequence` (pending)
   - Not a known atom step (read_card / put_down_card / verify_idle)
   - `has_cached_command_step`: false (not in plan.command_steps)
   - **Route: `verify_or_continue_sequence`**
   - `required_agent_task`: `verify_or_continue_sequence`

**Recommended next action (no robot execution):** The sequence `seq_view_right_hole_card` has completed its card-reading sub-task (both cards cached, robot idle, card returned to slot). The agent should advance the sequence to `verify_idle` or mark the sequence complete and transition to `idle` loop stage.

---

## Uncertain Fields

- `opponent_bet`: partial occlusion by robot arm at right edge
- `my_chips`, `opponent_chips`: angled perspective; brown chip counts estimated

---

## Output Files

| File | Status |
|---|---|
| `s_current/01_parsed_state.md` | written |
| `visual_raw/scene-stability-agent.md` | written |
| `visual_raw/turn-detection-agent.md` | written |
| `visual_raw/community-cards-agent.md` | written |
| `visual_raw/chip-recognition-agent.md` | written |
| `visual_raw/bet-recognition-agent.md` | written |
| `visual_raw/blind-button-recognition-agent.md` | written |
| `visual_raw/robot-behavior-agent.md` | written |
| `visual_summary.json` | written |
| `eval_report.md` | written |
