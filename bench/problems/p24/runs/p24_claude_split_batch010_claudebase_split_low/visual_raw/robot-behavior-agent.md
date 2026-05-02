# Robot Behavior Agent — State s21

## Visual Findings

The dexterous hand is extended over the table surface, positioned in the left-center area near the chip zone. The arm is lowered and angled toward the table. The fingers appear open and splayed, not in a gripping configuration. The hand does not appear to be holding a chip or card.

The chip layout on the table appears intact and countable. Multiple chip stacks are visible in the lower-center area of the frame, with denominations still separable. No chips appear scattered or mixed beyond normal arrangement. The hole-card area to the far left appears to have cards face-down in place.

Given context (loop_stage="to_recover", chip 10 dropped along the way, no chip pushed by finger, interrupted motion), the hand has come to rest in a non-idle extended pose but is not holding anything. The chip layout remains intact. This matches a retryable recovery condition: the push did not complete, but the layout is intact and the cached action can be retried.

```json
{
  "robot_idle": false,
  "hand_safe": true,
  "recovery_evidence": "The dexterous hand is extended over the chip area with fingers open and no chip held. The chip layout on the table is intact and countable, with denomination groups still separable. No card, button, or opponent object appears disturbed. The interrupted chip-push left the table in a parseable state consistent with a retryable recovery.",
  "reason": "Hand is settled away from rest pose, fingers open, not holding any chip or card. Chip layout is intact. Table state is safe and countable. Loop stage to_recover with a dropped chip mid-push and no chip displaced to the bet area matches a retryable miss. No human-help condition detected."
}
```
