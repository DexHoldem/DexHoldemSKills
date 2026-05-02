# Eval Report — p1_claude_split_batch010_claudebase_split_low

**State**: s0  
**Image**: s0/00_capture.jpg  
**Run mode**: split visual agents (parallel wave)  

## Visual Subagent Results

All 9 visual subagents were launched in a single parallel wave.

| Agent | Result | Confidence | Notes |
|---|---|---|---|
| scene-stability | stable=true | 0.82 | Single frame only; no prior frame for comparison |
| turn-detection | is_my_turn=true | 0.97 | White "Your Turn" button in robot seat band |
| community-cards | [] preflop | 0.92 | All 5 community slots face-down |
| chip-recognition | my=380, opp=410 | 0.40 | Low confidence; camera angle + occlusion |
| bet-recognition | my=60, opp=50 | 0.45 | Low confidence; partial robot-arm occlusion |
| blind-button | BB=robot, SB/D=opponent | 0.90 | Yellow BIG BLIND button on robot side; blue DEALER on opponent |
| held-card | null | 0.85 | Robot hand not holding card; cards face-down on table |
| robot-behavior | hand extended, no safety concern | 0.65 | Hand over opponent zone but not at rest |
| showdown-outcome | showdown=false, none | 0.78 | No face-up cards, no muck visible |

## Merged Table State

```
scene_stable:     true
is_my_turn:       true
street:           preflop
community_cards:  []
my_chips:         380    (uncertain — low confidence chip count)
opponent_chips:   410    (uncertain — low confidence chip count)
my_current_bet:   60     (uncertain — partial occlusion)
opponent_bet:     50     (uncertain — partial occlusion)
dealer:           opponent
small_blind:      opponent
big_blind:        robot
showdown:         false
```

## Router Decision

Given the merged state:
- `scene_stable=true` → proceed
- `loop_stage=idle` (from action_sequence.json)
- `is_my_turn=true` → proceed
- Hole card cache: both slots unknown/uncached

**Route**: `view_hole_card`  
**Reason**: Left hole card is not cached; robot must pick up and read the left card before a poker action can be selected.  
**Suggested action**: `{"action": "view_card", "position": "left"}`  
**Agent required**: No (executor handles the physical atom)

## Uncertain Fields

The following fields were flagged uncertain due to camera angle and robot-arm occlusion:
- `my_chips` (confidence 0.40)
- `opponent_chips` (confidence 0.40)
- `my_current_bet` (confidence 0.45)
- `opponent_bet` (confidence 0.45)

These will be resolved after the hole-card view sequence completes and a fresh capture is taken.

## Raw Evidence Files

All 9 agent evidence files written to:
`runs/p1_claude_split_batch010_claudebase_split_low/visual_raw/`

- scene-stability-agent.md
- turn-detection-agent.md
- community-cards-agent.md
- chip-recognition-agent.md
- bet-recognition-agent.md
- blind-button-recognition-agent.md
- held-card-recognition-agent.md
- robot-behavior-agent.md
- showdown-outcome-agent.md
