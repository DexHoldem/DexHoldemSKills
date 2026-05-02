# Chip Recognition — s_current

**Agent**: chip-recognition-agent
**Image**: s_current/00_capture.jpg

## Robot/Player Inventory (bottom seat area)

Lower-left group: approximately 3 red 5-chips visible.
Lower-right area (partially occluded by robot arm): approximately 1 blue 10-chip, 1 green 50-chip, 1 brown 100-chip.

Robot/player inventory estimate:
- Red (5): ~3
- Blue (10): ~1 (uncertain, partially occluded by robot arm)
- Green (50): ~1 (uncertain, partially occluded by robot arm)
- Brown (100): ~1 (uncertain, partially occluded by robot arm)

Estimated total: ~175 chips value. Count is uncertain; right-side chips are occluded by the robot arm.

**Note**: s30 showed {5:4, 10:3, 50:3, 100:3} = 500 total before the 100-chip push action. The current visual count (175) is significantly lower than expected (~400 after push). The chip count is likely unreliable due to occlusion.

## Opponent Inventory (top seat area)

Upper-left cluster visible:
- Red (5): 0 visible
- Blue (10): approximately 2 (uncertain)
- Green (50): approximately 1 (uncertain)
- Brown (100): approximately 2 (uncertain)

Estimated total: ~270 chips value. Group is partially angled and occluded.

**Result**:
- `my_chips`: ~175 (uncertain)
- `opponent_chips`: ~270 (uncertain)
- `uncertain_fields`: ["my_chips", "opponent_chips"]
