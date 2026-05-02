# Perception Eval Report

**Run ID:** p34_claude_split_scoped_quicktest_claude_sonnet_low  
**Frame:** s31/00_capture.jpg  
**Date:** 2026-05-02  
**Subagents:** 9 launched in parallel (1 wave)

## Scene Stability
- **Stable:** yes (confidence 0.91)
- Robot arm retracted from s30→s31; full table visible.

## Game State
| Field | Value | Confidence |
|-------|-------|------------|
| Street | river | 0.35 |
| Community cards | 8h, 6s, 6d, 6c, ? | 0.35 |
| Hole cards | 9d, 5d | 0.82 (from cache) |
| Robot turn | yes | 0.97 |
| Showdown | no | 0.35 |

## Positions
- Dealer: opponent | Small blind: opponent | Big blind: robot (confidence 0.88)

## Chips
| | Value | Confidence |
|---|---|---|
| Robot inventory | 90 | 0.30 |
| Opponent inventory | 225 | 0.30 |
| Robot bet | 120 | 0.45 |
| Opponent bet | 20 | 0.45 |
| Pot (estimated) | 140 | 0.45 |

## Robot Behavior
- Hand pose: idle | Action in progress: no | Safe: yes | Recovery needed: no (confidence 0.92)

## Notes
- Community card position 5 (rightmost) is partially occluded by the robot arm; unreadable.
- Chip counts have low confidence due to camera angle and partial arm occlusion of the upper-right table region.
- Hole cards carried from cache (s5/s15); no card held in current frame.
- No showdown indicators detected; opponent cards are face-down.

## Output Files
- `visual_raw/scene_stability.json`
- `visual_raw/community_cards.json`
- `visual_raw/held_cards.json`
- `visual_raw/turn_detection.json`
- `visual_raw/chip_counts.json`
- `visual_raw/bet_recognition.json`
- `visual_raw/blind_buttons.json`
- `visual_raw/robot_behavior.json`
- `visual_raw/showdown_outcome.json`
- `visual_summary.json`
- `eval_report.md`
