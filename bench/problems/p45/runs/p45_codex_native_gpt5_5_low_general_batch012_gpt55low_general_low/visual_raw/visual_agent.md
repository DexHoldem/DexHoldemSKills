Scene stability evidence:
Unstable. Compared `s41/00_capture.jpg` and `s42/00_capture.jpg`. The robot arm/hand is in a substantially different position between the two images, moving from across the middle-left table area to the right side near the community cards, so the previous action appears still in motion rather than settled. Cards and chips look generally stationary, and no human arm is actively on the table, but the robot pose change is large enough to mark the scene unstable.

Board and bet evidence:
Five community cards are visible left to right: Qs, Qh, 7d, Qc, and 7c.
My current bet area, left of the community cards: no bet chips visible. The nearby chips to the left appear to be inventory, not in the betting area.
Opponent bet area, right of the community cards: no bet chips visible. The chips on the upper/right player area appear to be inventory, not a bet area.
Uncertainty: none significant for the community-card count; bet areas look empty, though the robot/camera body partially blocks the far-right table edge.

Reasoning validation:
Wait. The scene is unstable (`scene_stable: false`), so no poker action should be recommended yet.
