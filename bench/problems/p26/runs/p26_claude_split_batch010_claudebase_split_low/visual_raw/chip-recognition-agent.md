# chip-recognition-agent — s23

Image: s23/00_capture.jpg

Table viewed from elevated angle. Bottom = robot seat; top = opponent seat. Inventory chips are those outside the central betting zone.

Robot inventory (bottom rail area): red(5)×5, blue(10)×3, green(50)×2, brown(100)×3.
Opponent inventory (top rail area): red(5)×3, blue(10)×2, green(50)×1, brown(100)×2.
Green(50) and brown(100) counts are uncertain due to shallow viewing angle and chip overlap.

```json
{
  "my_chips": {
    "5": 5,
    "10": 3,
    "50": 2,
    "100": 3
  },
  "opponent_chips": {
    "5": 3,
    "10": 2,
    "50": 1,
    "100": 2
  },
  "confidence": {
    "my_chips_red_5": "moderate",
    "my_chips_blue_10": "moderate",
    "my_chips_green_50": "low",
    "my_chips_brown_100": "moderate",
    "opponent_chips_red_5": "moderate",
    "opponent_chips_blue_10": "low",
    "opponent_chips_green_50": "low",
    "opponent_chips_brown_100": "low"
  }
}
```
