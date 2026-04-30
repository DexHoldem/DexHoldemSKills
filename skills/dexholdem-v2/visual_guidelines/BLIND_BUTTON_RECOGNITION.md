# Blind Button Recognition Guideline

Use this guideline once during preflight to identify dealer, small blind, and
big blind positions from the table image.

In this setup there are only two players. The small blind is tied to the dealer
button. The other player is the big blind.

## Inputs To Provide

Give the vision agent the preflight or first state image, usually
`s0/00_capture.jpg`.

Optionally also provide `TABLE_GEOMETRY.md` so the agent can orient robot/player
seat versus opponent seat.

Do not require the vision agent to read JSON files or produce JSON.

## What To Look For

Identify the physical circular buttons on the table:

- dealer button: usually a white button labeled `DEALER`,
- small blind button: may be a blue button labeled `SMALL BLIND`,
- big blind button: usually a yellow button labeled `BIG BLIND`.

The buttons can move between hands, but preflight needs the current initial
blind assignment for this session/hand.

## Two-Player Rule

Use this rule after locating the dealer button:

- the player with the dealer button is also the small blind,
- the other player is the big blind.

If a visible small-blind or big-blind button conflicts with the dealer rule,
say exactly what conflict you see instead of forcing an answer.

## Seat Names

Use only these seat names:

- `robot` - bottom-side robot/player seat,
- `opponent` - top-side human opponent seat,
- `unclear` - button cannot be localized safely.

Do not use poker table position names such as BTN, SB, BB, UTG, or CO in the
visual response.

## Response Style

Use concise plain language:

```text
Dealer/small blind is at the robot seat. The opponent is the big blind.
```

or:

```text
Dealer/small blind is at the opponent seat. The robot is the big blind.
```

or:

```text
Blind assignment is unclear. The dealer button is partly occluded and I cannot
safely determine which seat has it.
```

## Response Contract

Answer in plain language. Include:

- which seat has the dealer button,
- which seat is small blind,
- which seat is big blind,
- any uncertainty or button conflict.

Do not produce structured JSON. The coding agent will cache the result in
`hole_card_cache.json` using `state.py set-blinds`.
