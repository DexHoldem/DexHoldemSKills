# Held Card Recognition Guideline

Use this guideline when a vision-capable agent is asked to read a hole card
currently held by the robot dexterous hand.

This is separate from community-card recognition. Hole cards on the table are
usually face-down and must not be guessed. A hole card can be read only while
the dexterous hand is holding it with the face visible to the camera.

## Inputs To Provide

Give the vision agent:

- the current state image, usually `sN/00_capture.jpg`,
- optionally a crop around the dexterous hand/card if available,
- optionally the current action-sequence intent in plain language, such as
  "view left hole card" or "view right hole card".

Do not require the vision agent to read JSON files or produce JSON.

## Card Notation

Use rank + suit notation when the card is readable:

- ranks: `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `T`, `J`, `Q`, `K`, `A`
- suits: `h`, `d`, `c`, `s`

Examples:

- `Ah` = ace of hearts
- `Td` = ten of diamonds
- `7c` = seven of clubs

## Recognition Rules

- Read only a card visibly held by the dexterous hand.
- Do not read or guess face-down hole cards lying on the table.
- Do not infer the other hole card.
- If the card face is partly visible but uncertain, give the best read and say
  exactly what is uncertain.
- If rank or suit is not readable, say the held card is unreadable.
- If no card is clearly held, say no readable held card is visible.

The coding agent decides which cache slot to update from the action-sequence
intent. The vision agent should not guess left/right slot unless the prompt
explicitly asks it to inspect sequence context.

## Response Style

Use concise plain language:

```text
The dexterous hand is holding a readable card. It appears to be Ah.
```

or:

```text
The dexterous hand is holding a card, but the rank is occluded and the card is
not safely readable.
```

or:

```text
No readable held card is visible. The hole cards on the table are face-down and
should not be guessed.
```

## Response Contract

Answer in plain language. Include:

- whether the dexterous hand is holding a card,
- the card value if readable,
- which part is uncertain if not fully readable,
- whether the card should be treated as unreadable.

Do not produce structured JSON. The coding agent will update
`hole_card_cache.json` only when the card is readable and the sequence slot is
known.
