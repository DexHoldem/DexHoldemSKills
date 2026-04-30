# Table Geometry Guideline

Use this guideline when a vision-capable agent needs orientation before reading
cards, chips, bets, turn button, or robot behavior from a DexHoldem table
image.

## Inputs To Provide

Give the vision agent the current state image, usually `sN/00_capture.jpg`.
No previous image is required unless the question is about movement or scene
stability.

Do not require the vision agent to read JSON files or produce JSON.

## Camera Orientation

The camera looks diagonally across the table:

- robot/player seat: bottom side of the image,
- opponent seat: top side of the image,
- robot dexterous hand: usually enters from the right side,
- community-card row: long central horizontal row,
- robot hole cards: lower area near the robot/player seat,
- opponent hole cards: upper area near the opponent seat.

Use this camera-relative geometry instead of poker position names.

## Chip Geometry

The chips are not vertical stacks. They are unfolded flat on the felt as
individual visible chips, often in small clusters or short rows. Count visible
chip faces one by one.

There are four chip denominations, usually arranged left-to-right by color
within each player's inventory area:

- red -> 5
- blue -> 10
- green -> 50
- brown -> 100

Because the chips are unfolded, do not estimate stack height. Count the visible
chips in each color/denomination group.

## Main Zones

Use these zones as anchors:

- robot/player chip inventory: bottom seat zone, near the bottom rail and
  around the robot hole-card area.
- opponent chip inventory: top seat zone, near the opponent rail and around
  the opponent hole-card area.
- my current bet: flat chips in the central betting area on the left side of
  the community-card row.
- opponent current bet: flat chips in the central betting area on the right
  side of the community-card row.
- community cards: face-up shared cards across the central row.
- buttons: white/yellow/blue circular buttons are not chips unless clearly
  chip-sized and colored by denomination.

Inventory chips can sit close to hole cards, while bet chips sit closer to the
community-card row. If a chip group is ambiguous, say which zone is uncertain
instead of forcing a count.

## Response Contract

Answer in plain language. Include:

- the relevant zone names you used,
- whether chips are inventory chips or bet chips,
- any zone that is occluded or ambiguous.

Do not produce structured JSON. The coding agent will use this geometry when
combining individual visual observations.
