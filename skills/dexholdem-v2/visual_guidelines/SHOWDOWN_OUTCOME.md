# Showdown And Outcome Guideline

Use this guideline when a vision-capable agent is asked whether the hand has
entered showdown, whether the robot must reveal its hole cards, or whether the
robot has won or lost the hand.

## Inputs To Provide

Give the vision agent:

- the current state image, usually `sN/00_capture.jpg`,
- the current community-card read in plain language,
- the robot hole-card cache in plain language, if available,
- optionally previous state images if they help distinguish a fold from normal
  face-down hole cards,
- optionally the latest action or table event in plain language, such as
  "opponent folded", "opponent showed cards", or "river betting finished".

Do not require the vision agent to read JSON files or produce JSON. If JSON
cache files are provided, treat them as context and answer in plain language.

## What To Observe

Focus on cards and visible hand outcome, not robot motion:

- whether the opponent's two hole cards are face-up in the top/opponent hole
  card area,
- whether the robot's two hole cards are face-up in the bottom/robot hole card
  area,
- which face-up opponent cards are readable,
- which face-up robot cards are readable,
- whether a player has clearly folded or mucked,
- whether enough cards are known to compare the best Texas Hold'em hand.

Use the community cards from `COMMUNITY_CARDS.md`. Use cached robot hole cards
when the robot cards are still face-down but were previously viewed and cached.

## Stage Decisions

Say `show_hand` when the opponent has made their hole cards face-up, or the
hand has otherwise reached showdown, and the robot's hole cards still need to
be revealed or the outcome is not yet clear.

Say `win` only when one of these is clear:

- the opponent folded and the robot is the uncontested winner,
- all needed showdown cards are readable or cached, and the robot's best
  five-card Texas Hold'em hand is stronger than the opponent's.

Say `lose` only when one of these is clear:

- the robot folded,
- all needed showdown cards are readable or cached, and the opponent's best
  five-card Texas Hold'em hand is stronger than the robot's.

If the result is tied, unreadable, occluded, or depends on a card that cannot be
read or found in cache, do not force `win` or `lose`. Say exactly what is
missing or ambiguous so the main coding agent can keep the state in
`show_hand`, rerun visual parsing, wait, or request human help.

## Poker Comparison

Compare each player using the best five-card hand from their two hole cards and
the shared community cards. Apply ordinary Texas Hold'em hand ranking:

straight flush, four of a kind, full house, flush, straight, three of a kind,
two pair, one pair, high card. Use kickers when the hand category is the same.

Do not judge by a single "larger card" unless that is truly the deciding
kicker after making each player's best five-card hand.

## Response Style

Use concise plain language:

```text
The opponent's two hole cards are face-up and readable as Qh and Qd. The
robot's hole cards are still face-down, but the cache says Ah and Kc. With the
visible board 2c 7d Qs 9h Jh, the opponent has three queens and the robot has
ace high. The robot loses.
```

```text
The opponent appears to have folded; their cards are not face-up and no
showdown comparison is needed. The robot wins the hand uncontested.
```

```text
The opponent's cards are face-up, but the right opponent card is unreadable.
The robot should not be marked win or lose yet.
```

## Response Contract

Answer in plain language. Include:

- whether opponent hole cards are face-up,
- readable opponent card values,
- whether robot hole cards are face-up or must come from cache,
- the best hand comparison when enough information is available,
- the recommended loop-stage label: `show_hand`, `win`, or `lose`,
- any missing card, unreadable card, possible tie, fold ambiguity, or other
  reason not to decide the outcome.

Do not output structured JSON. The coding agent will convert the answer into
the parsed state's `loop_stage` and any compact table notes needed for routing.
