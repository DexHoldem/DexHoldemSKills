# DexHoldem Perception Eval Report

**Run ID:** p5_claude_split_batch010_claudebase_split_low  
**State evaluated:** s3  
**Source image:** s3/00_capture.jpg  
**Date:** 2026-05-02

---

## Visual Agents Run (Parallel Wave)

| Agent | Key Findings | Confidence |
|-------|-------------|------------|
| scene-stability-agent | scene_stable=false; robot hand moved between s2→s3, pick_card in progress | 0.82 |
| turn-detection-agent | is_my_turn=true; "Your Turn" button visible at robot seat | 0.90 |
| robot-behavior-agent | hand near table edge, settled low pose, no card visibly gripped, action_complete=false | 0.52 |
| community-cards-agent | community_cards=[] (all face-down, pre-flop) | 0.90 |
| chip-recognition-agent | my_chips={5:4,10:6,50:2,100:2}; opponent_chips={5:2,10:4,50:2,100:1} (uncertain, arm occlusion) | 0.45 |
| bet-recognition-agent | my_current_bet={5:2,10:2}; opponent_bet={10:3,100:2} (uncertain, layout ambiguity) | 0.45 |
| blind-button-recognition-agent | dealer=opponent, small_blind=opponent, big_blind=robot | 0.82 |

---

## Router Decision

**Input state context:**
- action_sequence.json: loop_stage=acting, intent=view_left_hole_card, current_step=pick_card (dispatched)
- Parsed state: scene_stable=false, loop_stage=acting

**Route:** `wait`  
**Reason:** scene_stable=false while loop_stage=acting. The scene-stability agent detected robot hand motion between s2 and s3 consistent with the pick_card atom being dispatched but not yet settled. Per router logic, the scene must stabilize before the dispatched step can be verified.

**Suggested action:**
```json
{"action": "wait", "reason": "scene_unstable", "sleep_seconds": 3}
```

No poker action reasoning was required (loop is in acting stage, not idle stage with turn).

---

## Output Files

| File | Status |
|------|--------|
| visual_raw/scene_stability.json | written |
| visual_raw/turn_detection.json | written |
| visual_raw/robot_behavior.json | written |
| visual_raw/community_cards.json | written |
| visual_raw/chip_recognition.json | written |
| visual_raw/bet_recognition.json | written |
| visual_raw/blind_button.json | written |
| visual_summary.json | written |
| eval_report.md | this file |
| s3/01_parsed_state.md | written |
| s3/02_action.md | written |

---

## Notes

- Chip and bet counts are marked uncertain in the parsed state due to arm occlusion and flat chip layout at low confidence (0.45). These fields appear in `uncertain_fields`.
- The robot behavior agent observed the hand in a low settled pose without a visible card in the gripper, suggesting either the pick_card motion is mid-flight or has completed without visible card capture — a follow-on capture after the wait will clarify.
- No reasoning subagent was invoked as the game state is not at the idle/choose_poker_action decision point.
