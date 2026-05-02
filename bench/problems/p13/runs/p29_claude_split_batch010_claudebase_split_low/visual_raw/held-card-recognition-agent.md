# Held Card Recognition Agent — s25

Image: s25/00_capture.jpg
Cache: hole_card_cache.json

No readable held card is visible in state s25. The robot hand is not showing a card face to the camera. Hole cards on the table are face-down and were not read.

Cache provides previously recognized values:
- Left slot: 9d (recognized at s5, confidence 1.0)
- Right slot: 5d (recognized at s15, confidence 1.0)

```json
{
  "hole_cards": ["9d", "5d"],
  "reason": "No readable held card is visible in state s25. The robot hand is not showing a card face to the camera. Hole cards are taken from the cache: left=9d (recognized at s5) and right=5d (recognized at s15), both at confidence 1.0. Table hole card positions are face-down and were not read."
}
```
