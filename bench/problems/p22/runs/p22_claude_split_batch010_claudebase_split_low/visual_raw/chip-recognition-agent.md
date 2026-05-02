# Chip Recognition Agent — s20/00_capture.jpg

## Scene Layout Notes
The robot arm and camera body enter from the lower-right and occlude a significant portion of the right side of the table. The central table shows a cluster of chips across the middle-lower felt. The "Your Turn" button is visible at the lower-left.

## Robot/Player Inventory Chips (bottom seat band)

| Denomination | Count | Confidence |
|---|---|---|
| Red (5) | ~4 | Reasonably clear |
| Blue (10) | ~4 | Reasonably clear |
| Green (50) | Unknown | Occluded by robot arm |
| Brown (100) | Unknown | Occluded by robot arm |

## Opponent Inventory Chips (top seat band)

| Denomination | Count | Confidence |
|---|---|---|
| Red (5) | ~4 | Uncertain (distance/angle) |
| Blue (10) | ~4 | Uncertain (distance/angle) |
| Green (50) | Unknown | Insufficient visibility |
| Brown (100) | Unknown | Insufficient visibility |

## Notes
- Green and brown counts cannot be reliably confirmed due to heavy occlusion from robot arm
- Visible red and blue counts (~4 each) are consistent with prior state {5:4, 10:4, 50:4, 100:4}
- Large chip cluster in central/middle-lower area is in the betting lane zone and excluded from inventory counts
- Carry forward prior state values for green (50:4) and brown (100:4) for both players
