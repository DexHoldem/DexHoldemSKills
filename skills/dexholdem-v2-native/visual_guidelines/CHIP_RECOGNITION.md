# Chip Recognition Guideline

Use this guideline when a vision-capable agent is asked to count the two
players' remaining chip inventories from a captured table image.

## Inputs To Provide

Give the vision agent the current state image, usually `sN/00_capture.jpg`.
No previous image is required unless occlusion makes the current inventory
count ambiguous.

Do not require the vision agent to read JSON files or produce JSON.

Chip recognition counts unfolded inventory chips for the robot/player and the
opponent. It does not count current bets; current bets are handled by
`BET_RECOGNITION.md` in this folder.

The vision model does not need to produce structured JSON. It should report
counts in plain language by denomination. The coding agent will parse those
counts into the state files.

## Geometry First

The chips are unfolded flat on the felt, not piled vertically. Count individual
visible chip faces in each color group. Do not estimate stack height.

If table orientation is unclear, first use `TABLE_GEOMETRY.md` in this folder.

## Denominations And Colors

Use this fixed left-to-right denomination order:

```text
5, 10, 50, 100
```

Colors:

- red chips -> 5
- blue chips -> 10
- green chips -> 50
- brown chips -> 100

## Robot/Player Inventory Chips

Robot/player inventory chips are the unfolded chip groups at the bottom seat
area, near the bottom rail and around the robot hole-card area. Do not include:

- chips in the current betting areas,
- opponent inventory chips,
- dealer/blind/turn buttons,
- community cards or hole cards.

## Opponent Inventory Chips

Opponent inventory chips are the unfolded chip groups at the top/opponent seat
area, near the top rail and around the opponent hole-card area. Do not include:

- opponent current bet,
- robot current bet,
- robot/player inventory chips,
- dealer/blind/turn buttons,
- community cards or hole cards.

## Unclear Counts

If a denomination is partially occluded, report the best visible count and say
that the count is uncertain.

If an entire inventory group is not visible enough to count, say that the group
is not countable from the image.

## Response Style

Use concise plain language:

```text
Robot/player inventory: about 4 red 5-chips, 3 blue 10-chips, 3 green 50-chips, and 3
brown 100-chips. The brown count is partly occluded.

Opponent inventory: about 3 red 5-chips, 5 blue 10-chips, 3 green 50-chips, and
4 brown 100-chips. Counts are approximate because the group is angled.
```

## Response Contract

Answer in plain language. Include:

- robot/player inventory counts by denomination,
- opponent inventory counts by denomination,
- which chip group or denomination counts are uncertain or not countable.

Do not include bet chips, pot chips, buttons, cards, or generic player arrays.
