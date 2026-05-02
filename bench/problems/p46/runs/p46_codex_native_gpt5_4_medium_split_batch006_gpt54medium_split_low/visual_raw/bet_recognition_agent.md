# bet_recognition_agent

Source image: `s45/00_capture.jpg`

Completed evidence:

My current bet:
- `red (5)`: 2
- `blue (10)`: 0 clearly countable
- `green (50)`: 1
- `brown (100)`: 3
- Confidence: medium
- Ambiguity: the right-side betting cluster is partly occluded by the robot/camera housing, so one chip on the far right could be `blue (10)` instead of the counted `green (50)`. If that chip is actually blue, then this would be `green 0, blue 1`.

Opponent bet:
- `red (5)`: 0
- `blue (10)`: 2
- `green (50)`: 2
- `brown (100)`: 3
- Confidence: medium
- Ambiguity: the opponent betting area is partially covered by the robot arm. The three-chip brown group on the right is fairly clear; the left mixed group appears to be `blue, green, blue, green`, but one of those left-group chips could be misread because of overlap.

Notes:
- Counted only the two current betting areas near the community cards.
- Did not include chip stacks by either player’s hole cards, blinds/button area, or any inventory stacks.
