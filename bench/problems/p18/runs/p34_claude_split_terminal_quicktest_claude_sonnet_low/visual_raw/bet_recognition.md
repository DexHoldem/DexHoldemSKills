# Bet Recognition — s_current

**Agent**: bet-recognition-agent
**Image**: s_current/00_capture.jpg

## My Current Bet Area (left of community cards)

Approximately 2 red (5) chips and 1 blue (10) chip grouped in the betting zone to the left of the community cards.

Estimated value: ~20 chips. Count is moderately uncertain due to chip overlap and camera angle.

**Note**: s30 showed my_current_bet = {10:1, 50:1, 100:1} = 160, and the robot was pushing an additional 100 chip (raise). Expected bet after push: ~260–270. Visual count of ~20 is significantly lower than expected. Likely the visual agent is miscounting occluded chips.

## Opponent Bet Area (right of community cards)

Approximately 1 red (5) chip and 1 blue (10) chip. The right portion is partially occluded by the robot arm.

Estimated value: ~15 chips. Count is uncertain and potentially incomplete.

**Note**: s30 showed opponent_bet = {5:2, 50:1, 100:1} = 160. Expected ~160. Visual count of ~15 is much lower, likely due to occlusion.

**Result**:
- `my_current_bet`: ~20 (uncertain, likely undercount due to occlusion)
- `opponent_bet`: ~15 (uncertain, likely undercount due to occlusion)
- `uncertain_fields`: ["my_current_bet", "opponent_bet"]
