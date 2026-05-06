# Community Card Recognition Guideline

Use this guideline when a vision-capable agent is asked to read the shared
community cards from a captured table image.

## Inputs To Provide

Give the vision agent the current state image, usually `sN/00_capture.jpg`.
No previous image is required unless comparing frames helps determine whether a
card was just dealt or moved.

Do not require the vision agent to read JSON files or produce JSON.

Community cards are the shared board cards in the center of the table. They are
the only source for deriving the poker board stage in V2.

The vision model does not need to produce structured JSON. It should describe
how many community cards are visible, read any clear rank/suit values, and say
which cards are uncertain. The coding agent will parse that response into the
state files.

Do not ask the vision model to output a separate `street` field. The poker
stage is derived from the number of visible community cards.

## Card Notation

Use rank + suit notation when a card is readable:

- ranks: `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `T`, `J`, `Q`, `K`, `A`
- suits: `h`, `d`, `c`, `s`

Examples:

- `Ah` = ace of hearts
- `Td` = ten of diamonds
- `7c` = seven of clubs

## Deriving Board Stage

The coding agent can derive the poker stage from the count:

- 0 cards -> preflop
- 3 cards -> flop
- 4 cards -> turn
- 5 cards -> river

## Recognition Rules

- Read only face-up cards in the shared board area.
- Do not include robot hole cards or opponent hole cards.
- Do not include folded/mucked opponent hole cards. A fold often appears as the
  opponent's two face-down hole cards moved away from their normal top-seat
  hole-card position and placed onto or near the community-card lane, compared
  with the first or previous stable states. Those face-down moved cards are not
  community cards.
- Do not guess face-down cards.
- Keep board order left-to-right as seen on the table.
- If a card is partially occluded but rank/suit is still reasonably clear,
  report the best read and say it is uncertain.
- If a card is too blurry or occluded, preserve its position by saying that the
  card is visible but unreadable.

## Response Style

Use a short natural-language answer:

```text
No community cards are visible.
```

or:

```text
Three community cards are visible from left to right. The first looks like 7d,
the second is unreadable, and the third looks like Kc. The middle card is
uncertain.
```

or:

```text
Five community cards are visible. The first four are 7d, 6s, 7c, Kc; the fifth
card is too blurry to read.
```

## Response Contract

Answer in plain language. Include:

- how many community cards are visible,
- the left-to-right card read for each visible position,
- which positions are unreadable or uncertain.

Do not include hole cards, do not output a `street` field, and do not invent
hidden or face-down card values.
