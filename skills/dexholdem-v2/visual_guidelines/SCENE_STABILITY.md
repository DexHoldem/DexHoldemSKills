# Scene Stability Guideline

Use this guideline when a vision-capable agent is asked to decide whether the
latest captured scene is stable enough for the main coding agent to continue.

## Inputs To Provide

Give the vision agent:

- the current state image, usually `sN/00_capture.jpg`,
- the previous state image, usually `sN-1/00_capture.jpg`,
- optionally older state images if the last two frames are ambiguous,
- optionally the previous action or action-sequence note, if available.

Do not require the vision agent to read JSON files or produce JSON.

Scene stability is a visual judgment used before the main agent chooses the
next action. It is not an absolute property of the table, and it is not
guaranteed just because a cancel/reset prefix was sent.

The vision model does not need to produce structured JSON. It should explain,
in plain language, whether the latest scene looks stable and why. The coding
agent will parse that response into the state files.

## Key Idea

Judge stability by comparing the two most recent state images:

```text
sN-1/00_capture.jpg
sN/00_capture.jpg
```

The vision model or vision agent may inspect older states when the last two
frames are ambiguous, but the final decision should answer whether the latest
frame is safe for the main agent's next decision.

## Stable

Call the scene stable only when:

- the previous action appears finished,
- the robot hand has returned to a near-idle pose or another clearly settled
  pose,
- the robot is not doing large movement,
- cards and chips are not visibly moving,
- unfolded chip groups are not being rearranged,
- no human arm is substantially on the table organizing, moving, or blocking
  cards/chips,
- the latest image is clear enough for the main agent to use.

Small visual differences are allowed. Lighting changes, tiny camera noise, or a
slightly different human posture do not make the scene unstable by themselves.
Humans move quickly, so do not over-focus on small human motion outside the
active table area.

## Unstable

Call the scene unstable when:

- the robot arm is mid-motion, blurred, reaching, or still settling,
- the robot is holding or moving a card/chips and the action is not clearly
  complete,
- cards or chips changed position between the two recent frames,
- a human arm/hand is largely on the table and appears to be organizing,
  moving, or blocking cards/chips,
- the latest frame is too occluded to determine whether the action finished,
- the robot looks stuck against an object or table feature.

If the robot may be stuck or has hit something, mark the scene unstable and let
the higher-level state machine escalate to human help after repeated unstable
captures. This guideline does not define the human-help escalation policy.

## Cancel And Reset Prefix

Most executable actions are prefixed with cancel/reset behavior:

- send cancel / Ctrl+C,
- reset the robot hand toward its init pose,
- then execute the requested action.

This prefix is part of the action execution flow. It should not be treated as a
standalone action that automatically makes the scene stable.

The scene becomes stable only after the full action sequence has visually
finished and the robot has stopped large movement. For `put_down_card`, the
reset prefix may be skipped because resetting while holding a card can drop it;
the vision check must account for that special case.

## Vision Agent Procedure

1. Open the current image `sN/00_capture.jpg`.
2. Open the previous image `sN-1/00_capture.jpg`.
3. Compare the robot arm, dexterous hand, cards, chips, and turn marker. Check
   human arms only for large table-blocking or object-moving behavior.
4. If the last two frames disagree but the reason is unclear, optionally inspect
   `sN-2/00_capture.jpg` or earlier state images.
5. Answer in plain language:
   - stable or unstable,
   - which frames were compared,
   - the concrete visual reason,
   - any notable uncertainty.

Example stable response:

```text
Stable. Compared s4/00_capture.jpg and s5/00_capture.jpg. The robot hand is
near idle, no card or chip movement is visible, and no human arm is changing the
table.
```

Example unstable response:

```text
Unstable. Compared s4/00_capture.jpg and s5/00_capture.jpg. A human arm is
substantially on the table and appears to be moving chips, so the table state
may still be changing.
```

## Response Contract

Answer in plain language. Include:

- `Stable` or `Unstable` as the first word,
- which images were compared,
- the concrete visual reason,
- any uncertainty that matters.

Do not decide the robot's next action. The coding agent will use the response
to choose wait, continue the current sequence, retry, or human help.

## Agent Use

If the scene is unstable, the next action should normally be `wait`, not a
robot movement or poker decision.

Repeated unstable states may indicate the robot is stuck, the table is blocked,
or a human is still acting. Escalation should be handled by the higher-level
state cache and action policy.
