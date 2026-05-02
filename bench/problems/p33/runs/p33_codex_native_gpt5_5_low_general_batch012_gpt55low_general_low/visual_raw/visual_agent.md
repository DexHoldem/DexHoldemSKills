# Visual Evidence

Source image:
- `s30/00_capture.jpg`

Independent visual agent findings:

## Pass 1
Direct answer: the scene appears stable enough to parse the board and several chip/button markers, but the right side is heavily occluded by the robot/camera hardware. The active turn marker is visible at the lower-left seat area.

Table Geometry
- Camera view is angled from the lower/front edge of the table toward the far player.
- Visible seat labels include `5` near lower-right/middle, `6` lower-left and upper-left, and `9` upper-left/far-left.
- Robot/camera hardware occupies the right side of the frame and blocks parts of the right player area and some chips/cards.

Scene Stability
- Image is sharp enough for major objects: community cards, chips, blind button, and turn marker.
- No obvious motion blur on the table surface.
- Main occlusion: large black robot/camera assembly on the right, covering some seat areas and possible bets.

Turn Status
- A white circular marker reading `Your Turn` is clearly visible near the lower-left seat area, close to the `6` label.
- Suggested parsed field: `turn_marker_visible: true`, `active_turn: hero/lower-left seat area`.
- Uncertainty: exact seat identity depends on the table geometry convention, but visually the marker is at the lower-left player position.

Community Cards
Five community cards are visible in the center row:
- `Qh` or `Qd` uncertain red queen; appears most likely queen of hearts because the pips look heart-shaped.
- `7d`
- `6s`
- `3c`
- A fifth card at far right is partially occluded by the robot/camera; it appears to be a black club card, likely `3c`, but the rank is not fully reliable.

Suggested parsed community cards with uncertainty:
- `Q? red`, `7d`, `6s`, `3c`, `?c`
- More confidence: middle three are `7d`, `6s`, `3c`.

Visible Hole Cards
- Several face-down card backs are visible at player positions.
- No clear face-up hole cards are visible.
- Do not infer any hidden cards.

Button / Blinds
- A yellow `BIG BLIND` button is clearly visible near the lower-middle/right seat area, close to the `5` label.
- A white `DEALER` button is visible near the upper-middle area, slightly right of center.
- A blue `SMALL BLIND` button is visible just above/behind the dealer button near the upper-middle area.
- Suggested parsed fields:
  - `dealer_button_visible: true`
  - `small_blind_button_visible: true`
  - `big_blind_button_visible: true`

Chip Stacks / Bets
- Multiple chip stacks are visible around seats and near the board.
- Lower-left/front player area: several red/white chips and blue/white chips, including visible denominations that look like `5` and `10`; exact count is uncertain due to stacking and angle.
- Lower-right/front-right area: a visible cluster of chips with denominations including `50` and `100`, partly occluded by robot/camera.
- Near the center/community-card area: a small stack or bet pile is visible below/right of the board, with black/white and red/white chips; exact amount unclear.
- Upper-middle/far side: several chip stacks and buttons near face-down cards; counts are difficult because chips overlap and are partially occluded.
- Upper-left/far-left: red/white and blue/white chip clusters are visible near seat labels `9`/`6`.

Uncertainties
- Exact chip totals cannot be reliably counted from this single angled frame.
- Right-side player area and any cards/chips there are partially blocked by the robot/camera.
- The far-right community card is partially occluded and should be treated as uncertain.
- More images from a cleaner overhead angle would improve chip counting, seat mapping, and card confirmation.

## Pass 2
Direct answer: the scene appears stable enough to parse the board and several chip/button markers, but the right side is heavily occluded by the robot/camera hardware. The active turn marker is visible at the lower-left seat area.

Table Geometry
- Camera view is angled from the lower/front edge of the table toward the far player.
- Visible seat labels include `5` near lower-right/middle, `6` lower-left and upper-left, and `9` upper-left/far-left.
- Robot/camera hardware occupies the right side of the frame and blocks parts of the right player area and some chips/cards.

Scene Stability
- Image is sharp enough for major objects: community cards, chips, blind button, and turn marker.
- No obvious motion blur on the table surface.
- Main occlusion: large black robot/camera assembly on the right, covering some seat areas and possible bets.

Turn Status
- A white circular marker reading `Your Turn` is clearly visible near the lower-left seat area, close to the `6` label.
- Suggested parsed field: `turn_marker_visible: true`, `active_turn: hero/lower-left seat area`.
- Uncertainty: exact seat identity depends on the table geometry convention, but visually the marker is at the lower-left player position.

Community Cards
Five community cards are visible in the center row:
- `Qh` or `Qd` uncertain red queen; appears most likely queen of hearts because the pips look heart-shaped.
- `7d`
- `6s`
- `3c`
- A fifth card at far right is partially occluded by the robot/camera; it appears to be a black club card, likely `3c`, but the rank is not fully reliable.

Suggested parsed community cards with uncertainty:
- `Q? red`, `7d`, `6s`, `3c`, `?c`
- More confidence: middle three are `7d`, `6s`, `3c`.

Visible Hole Cards
- Several face-down card backs are visible at player positions.
- No clear face-up hole cards are visible.
- Do not infer any hidden cards.

Button / Blinds
- A yellow `BIG BLIND` button is clearly visible near the lower-middle/right seat area, close to the `5` label.
- A white `DEALER` button is visible near the upper-middle area, slightly right of center.
- A blue `SMALL BLIND` button is visible just above/behind the dealer button near the upper-middle area.
- Suggested parsed fields:
  - `dealer_button_visible: true`
  - `small_blind_button_visible: true`
  - `big_blind_button_visible: true`

Chip Stacks / Bets
- Multiple chip stacks are visible around seats and near the board.
- Lower-left/front player area: several red/white chips and blue/white chips, including visible denominations that look like `5` and `10`; exact count is uncertain due to stacking and angle.
- Lower-right/front-right area: a visible cluster of chips with denominations including `50` and `100`, partly occluded by robot/camera.
- Near the center/community-card area: a small stack or bet pile is visible below/right of the board, with black/white and red/white chips; exact amount unclear.
- Upper-middle/far side: several chip stacks and buttons near face-down cards; counts are difficult because chips overlap and are partially occluded.
- Upper-left/far-left: red/white and blue/white chip clusters are visible near seat labels `9`/`6`.

Uncertainties
- Exact chip totals cannot be reliably counted from this single angled frame.
- Right-side player area and any cards/chips there are partially blocked by the robot/camera.
- The far-right community card is partially occluded and should be treated as uncertain.
- More images from a cleaner overhead angle would improve chip counting, seat mapping, and card confirmation.

