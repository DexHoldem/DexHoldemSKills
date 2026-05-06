# Table Geometry Guideline

Use this as a short fixed-layout reference for DexHoldem visual prompts.

## Orientation

The camera looks diagonally from the robot/player side toward the opponent.

- Robot/player seat: bottom of image.
- Opponent seat: top of image.
- Robot hand/camera body: usually enters from the right and may occlude the
  right side of the table.
- Community cards: central row across the middle-lower table.
- Robot hole cards: lower area near the robot/player seat.
- Opponent hole cards: upper area near the opponent seat.

Avoid bare "left" and "right" for player ownership. Prefer
`bottom/robot side`, `top/opponent side`, `lower-left of board`, or
`upper-right of board`.

## Approximate Regions

Use these as rough priors for the usual 1920x1080 image. Trust visible table
markings over exact numbers if the camera shifts.

Coordinates are normalized `(x_min-x_max, y_min-y_max)`, with image left/top as
`0%`.

- Felt/table: `(0-100%, 40-95%)`
- Robot/player seat band: `(0-100%, 62-95%)`
- Opponent seat band: `(15-75%, 34-54%)`
- Community-card row: `(25-70%, 52-66%)`
- Robot hole cards: `(45-72%, 70-86%)`
- Opponent hole cards: `(35-55%, 42-52%)`
- Robot-turn button area: `(7-17%, 73-86%)`
- Deck at far left edge: `(0-5%, 58-66%)`
- Common robot/camera occlusion: `(62-100%, 0-55%)`

## Chips

Chips are flat/unfolded, not stacked. Count visible chip faces one by one.

Denominations:

- red = 5
- blue = 10
- green = 50
- brown = 100

Buttons are not chips. White/yellow/blue labeled round markers are turn,
dealer, small blind, or big blind buttons unless they clearly match chip
denomination styling.

## Zones

- Robot inventory chips: bottom seat band, near lower rail and robot hole-card
  area, outside the central betting lane.
- Opponent inventory chips: top seat band, near opponent hole-card area,
  outside the central betting lane.
- Robot current bet: central betting lane on the lower/robot side of the
  community-card row, between robot inventory and board.
- Opponent current bet: central betting lane on the upper/opponent side of the
  community-card row, between opponent inventory and board.
- Community cards: face-up shared cards in the central row.
- Deck: far-left edge; not hole cards or community cards.

If a chip/card/button zone is ambiguous or occluded, say which zone is uncertain
instead of forcing a count or card read.

## Response Contract

Answer in plain language. Mention:

- which zone names you used,
- whether chips are inventory chips or bet chips,
- any occluded or ambiguous zones.

Do not output JSON.
