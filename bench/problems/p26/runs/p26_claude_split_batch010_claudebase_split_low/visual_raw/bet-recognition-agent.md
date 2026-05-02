# bet-recognition-agent — s23

Image: s23/00_capture.jpg

Community card row anchors the left/right split of betting areas. Robot seat is bottom-left; betting area is left of community cards. Opponent betting area is right of community cards (partially occluded by robot arm).

Left bet zone (my current bet): cluster with approximately 2 red(5) and 2 blue(10) chips visible.
Right bet zone (opponent bet): approximately 2 red(5) and 1 blue(10) chip visible; robot arm partially occludes this zone.

No green(50) or brown(100) chips visible in either betting area.

```json
{
  "my_current_bet": {
    "5": 2,
    "10": 2,
    "50": 0,
    "100": 0
  },
  "opponent_bet": {
    "5": 2,
    "10": 1,
    "50": 0,
    "100": 0
  },
  "confidence": {
    "my_current_bet": "low - chips clustered and angled perspective makes exact count uncertain",
    "opponent_bet": "low - robot arm partially occludes right betting area"
  }
}
```
