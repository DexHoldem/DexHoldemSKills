# Scene Stability Agent — State s21

## Visual Findings

Compared s20/00_capture.jpg (loop_stage: "acting", robot pushing chips) and s21/00_capture.jpg (loop_stage: "to_recover").

In s20, the robot arm is in a lower, more compact pose with the dexterous hand near the center chip area. In s21, the robot arm has moved substantially — it is now elevated and extended horizontally outward, with the dexterous hand reaching toward the left portion of the table. The arm is clearly not in an idle or settled pose; it is in a mid-reach extended configuration consistent with an interrupted chip-push motion. Chip positions also appear to differ between frames. The human's posture has also changed between frames.

Given loop_stage="to_recover" confirming motion was interrupted mid-sequence, and the robot arm's current extended-over-table position, the scene is Unstable.

```json
{
  "scene_stable": false,
  "reason": "Robot arm has moved substantially between s20 and s21 and is currently in a non-idle extended pose over the table, consistent with an interrupted chip-push motion. The dexterous hand is reaching outward over the chip area and has not returned to an atom_idle-compatible settled pose. Chip positions also differ between frames. loop_stage is to_recover confirming motion was interrupted mid-sequence."
}
```
