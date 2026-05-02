# Eval Report

Current state: `s22`

Perception outcome:
- The scene is not stable enough to treat as settled.
- It is not our turn.
- No community cards are face-up.
- Dealer button is on the opponent side.
- Small blind is opponent.
- Big blind is robot.

Inventory evidence:
- Robot/player chips: red 5 = 5, blue 10 = 4, green 50 = 5 uncertain, brown 100 = 5 uncertain.
- Opponent chips: red 5 = 4, blue 10 = 5, green 50 = 5 uncertain, brown 100 = 4 uncertain.

Reasoning validation:
- No Texas Hold'em poker-action reasoning is needed.
- Supported next step is `wait`.
- No robot action was executed.

Notes:
- Raw evidence files were written under `visual_raw/`.
- The chip counts include uncertainty on the green and brown stacks because of occlusion.
