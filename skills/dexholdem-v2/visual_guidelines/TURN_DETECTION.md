# Turn Detection Guideline

Use this guideline when a vision-capable agent is asked to determine whether it
is the robot/player's turn from a captured table image.

## Inputs To Provide

Give the vision agent the current state image, usually `sN/00_capture.jpg`.
No previous image is required unless the white turn button is hard to localize.

Do not require the vision agent to read JSON files or produce JSON.

Turn detection is based only on the small white physical turn button.

The vision model does not need to produce structured JSON. It should simply say
whether the white turn button indicates it is the robot/player's turn. The
coding agent will convert that answer into the boolean `is_my_turn` field.

Do not infer the robot's turn from dealer order, betting order, opponent body
posture, chip positions, or poker action prompts. Those cues may be useful for
strategy, but they should not decide turn ownership in this setup.

## Positive Case

Say it is our turn when the white button labeled like "Your Turn" is at the
robot/player seat area.

In the usual camera view, the robot/player seat is the bottom side of the table.
If the button is near the bottom-left robot seat area, the turn is true.

## Negative Case

Say it is not our turn when the white turn button is at another player's seat
area.

For example, `bench/bench_raw/50.jpg` is a clear false case: the white turn
button is on the opponent/top side of the table, not near the robot seat.

## Occluded Or Unclear Case

If the button is not visible or is too occluded/blurry to localize, say that it
is not safely identifiable. The coding agent should normally treat that as not
our turn and wait or ask for human confirmation.

## Response Style

Use a short natural-language answer:

```text
It is our turn. The white "Your Turn" button is near the robot seat at the
bottom-left of the table.
```

or:

```text
It is not our turn. The white turn button is on the opponent side of the table.
```

Keep this separate from available poker actions. The button answers only:
"is it our turn to act now?"

## Response Contract

The answer must make one of these plain-language judgments:

- it is our turn,
- it is not our turn,
- the turn button is not safely identifiable.

Do not report confidence or available actions.
