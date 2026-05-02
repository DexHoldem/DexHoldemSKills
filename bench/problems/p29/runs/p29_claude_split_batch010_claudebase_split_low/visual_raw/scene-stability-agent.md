# Scene Stability Agent — s25

Image: s25/00_capture.jpg (compared with s24/00_capture.jpg)

Community cards changed between frames indicating a card-dealing or placement action occurred. In s25, cards are settled on the table with no mid-transfer objects visible, no motion blur on the robot, and the robot hand is elevated in a post-action pose. The human is not blocking the table. Moderate uncertainty exists because the robot arm is not in a fully obvious idle home position, but no active motion or card/chip transfer is visible.

```json
{
  "scene_stable": true,
  "reason": "Compared s24/00_capture.jpg and s25/00_capture.jpg. Community cards changed between frames indicating a card-dealing or placement action occurred. In s25, cards are settled on the table with no mid-transfer objects visible, no motion blur on the robot, and the robot hand is elevated in a post-action pose. The human is not blocking the table. Moderate uncertainty exists because the robot arm is not in a fully obvious idle home position, but no object is in transit and no motion blur is present.",
  "frames_compared": ["s24/00_capture.jpg", "s25/00_capture.jpg"],
  "uncertainty": "Robot arm in s25 is elevated and not in a clearly defined idle/home pose, but no object is in transit and no motion blur is present."
}
```
