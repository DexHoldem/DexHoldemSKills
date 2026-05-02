# scene-stability-agent — s23

Image: s23/00_capture.jpg

Both s22 and s23 frames are visually nearly identical. The robot dexterous hand is in the same resting/near-idle position above the upper-right table area. No card or chip movement is visible between the two frames. The chip layout across both seat bands is unchanged. The community card zone remains the same. The human player is leaning over the table in a similar posture. No motion blur or mid-transfer artifacts are visible.

```json
{
  "scene_stable": true,
  "confidence": 0.92,
  "frames_compared": ["s22/00_capture.jpg", "s23/00_capture.jpg"],
  "robot_hand_settled": true,
  "cards_stable": true,
  "chips_stable": true,
  "human_arm_blocking": false,
  "visual_diff_summary": "Frames are nearly identical. Robot hand is stationary in a near-idle pose. No chip or card position changes detected between the two frames.",
  "uncertainty": "Minor: robot hand fingertips hover slightly above the upper opponent-side table region — settled idle pose, not active motion."
}
```
