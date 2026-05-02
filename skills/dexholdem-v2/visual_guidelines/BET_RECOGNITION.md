# Bet Recognition Guideline

Use this guideline when a vision-capable agent is asked to count chips currently
placed in the two betting areas from a captured table image.

## Inputs To Provide

Give the vision agent the current state image, usually `sN/00_capture.jpg`.
No previous image is required unless recent movement makes current bet
placement ambiguous.

Do not require the vision agent to read JSON files or produce JSON.

The table has two players. Bet recognition only counts unfolded chips currently
placed in the betting areas near the community cards.

The vision model does not need to produce structured JSON. It should report
counts in plain language by side and denomination. The coding agent will parse
those counts into `my_current_bet` and `opponent_bet`.

Do not model a generic pot or a generic players array in parsed visual state.
Keep the two bet areas separate. Later collection actions may pull chips from
`opponent_bet` and `my_current_bet` as distinct source zones, so do not merge
them into one pot count.

## Denominations And Colors

Use the same denomination order as inventory chip recognition:

```text
5, 10, 50, 100
```

Colors:

- red chips -> 5
- blue chips -> 10
- green chips -> 50
- brown chips -> 100

## Table Geometry

Use the community-card row as the anchor:

- my current bet: chips on the left side of the community cards,
- opponent bet: chips on the right side of the community cards.

The chips are flat on the felt, not vertical stacks. Count individual visible
chip faces in these betting areas. If table orientation is unclear, first use
`TABLE_GEOMETRY.md` in this folder.

Only count chips placed in these betting areas. Do not include:

- the robot/player inventory chips near the bottom seat,
- the opponent inventory chips near the top seat,
- dealer/blind/turn buttons,
- chips that clearly belong to an inventory group rather than a bet area,
- community cards or hole cards.

## No Chips Visible

If no chips are visible in a betting area, say that no bet chips are visible on
that side.

## Unclear Counts

If a betting area is partially occluded or angled, report the best visible count
and say that the count is uncertain.

## Robot Hand Occlusion

The dexterous hand may partially block the opponent's betting area when it is in
a near-idle pose (close to but not exactly the initial pose). If the robot hand
occludes the opponent bet area:

- Report which part of the betting area is blocked.
- Give the best visible count for any chips that are countable.
- Mark the opponent bet count as uncertain due to occlusion.

When bet recognition reports occlusion by the robot hand, the main agent should
consider dispatching `reset_to_init` to move the hand to its true initial pose,
then capture a fresh image for a clear view of the betting areas.

## Derived Betting Math

`to_call` is derived later from the two bet counts. Do not ask the vision model
to compute or report `to_call`.

## Response Style

Use concise plain language:

```text
My current bet area, left of the community cards: no chips visible.
Opponent bet area, right of the community cards: no chips visible.
```

or:

```text
My current bet area: two red 5-chips, no blue, green, or brown chips visible.
Opponent bet area: about two red 5-chips, one blue 10-chip, no green chips, and
two brown 100-chips. The opponent bet count is uncertain because the right side
is angled.
```

## Response Contract

Answer in plain language. Include:

- my current bet counts by denomination,
- opponent bet counts by denomination,
- which side or denomination counts are uncertain or not countable.

Do not count inventory chips, do not report `to_call`, and do not model a
generic pot.
