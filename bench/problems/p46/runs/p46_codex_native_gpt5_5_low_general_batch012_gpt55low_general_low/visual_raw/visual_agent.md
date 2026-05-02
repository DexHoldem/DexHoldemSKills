Merged visual evidence for s45/00_capture.jpg

Source agents:
- Hubble: table geometry, board, chips, turn/button markers
- McClintock: hole cards, blind/dealer cues, scene stability

Evidence:
- Community cards visible across the board: Qs, Qh, 7d, 6s, 7c.
- Hero hole cards visible at the near/bottom seat: Qd and 5d.
- Turn indicator visible: a white disc reading "Your Turn" near the lower-left player area.
- Blind/dealer markers visible: yellow "BIG BLIND" near seat 5, white "DEALER" near the upper-center/far area, and a blue blind-style disc near the upper-center that is likely "SMALL BLIND" but not fully legible.
- Chip denominations visible on the felt include 5, 10, 50, and 100.
- The scene appears stable with no obvious motion blur.
- A robot arm occludes part of the right side of the table, but no active grasping or object movement is evident in the frame.

Uncertainties:
- Exact chip totals and bet amounts are not readable with confidence.
- Far/top player's hole cards are present but not legible enough to parse.
- The blue blind button text near the top-center is partially obscured.

Suggested parsed fields:
```text
community_cards: [Qs, Qh, 7d, 6s, 7c]
hero_visible_cards: [Qd, 5d]
turn_indicator: "Your Turn"
visible_buttons:
  dealer: upper-center/far player area
  big_blind: lower-middle/right near seat 5
  small_blind: upper-center, uncertain text
chip_denominations_seen: [5, 10, 50, 100]
```
