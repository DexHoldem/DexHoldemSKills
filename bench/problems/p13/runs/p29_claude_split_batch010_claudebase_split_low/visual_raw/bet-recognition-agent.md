# Bet Recognition Agent — s25

Image: s25/00_capture.jpg

Robot/player bet area (lower-central lane): ~1 blue(10) + ~2 red(5+5) = 20.
Opponent bet area (upper-central lane): ~2 brown(100+100) + ~1 red(5) ≈ 205.
Opponent count uncertain due to robot arm occlusion in upper-right table region and chip overlap.

```json
{
  "my_current_bet": 20,
  "opponent_bet": 205,
  "reason": "Robot/player bet area (lower-central lane): 1 blue (10) + 2 red (5+5) = 20. Opponent bet area (upper-central lane): approximately 2 brown chips (100+100) + 1-2 red chips (~5) = ~205. Opponent count is uncertain due to robot arm occlusion in upper-right table region and chip overlap. No green chips observed in either betting area. Inventory chips at bottom and top seat bands excluded.",
  "uncertain_fields": ["opponent_bet"]
}
```
