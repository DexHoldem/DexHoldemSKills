# Robot Behavior Guideline

Use this guideline when a vision-capable agent is asked to describe what the
robot dexterous hand is physically doing and whether the current action has
created a physical failure that needs human help.

## Inputs To Provide

Give the vision agent:

- the current state image, usually `sN/00_capture.jpg`,
- optionally the previous state image if motion or sequence progress is
  ambiguous,
- optionally the current `action_sequence` intent in plain language, such as
  "view left hole card", "put down left hole card", or "push chips",
- optionally the recent `action_sequence` step statuses,
- optionally the current `hole_card_cache` in plain language, for example
  "left card is cached as Ah; right card is unknown",
- optionally earlier state images if the agent needs to compare whether cards
  or chip groups were disturbed.

Do not require the vision agent to read JSON files or produce JSON.
If JSON cache files are provided, treat them as context and answer in plain
language.

## What To Observe

Focus on the physical robot arm and dexterous hand:

- whether the hand is near its initial/rest pose,
- whether the hand is reaching, moving, blurred, or mid-action,
- whether the hand is holding a card,
- whether the hand is holding or pushing chips,
- whether the hand appears stuck, blocked, or in contact with something,
- whether the hand occludes cards, chips, the turn button, or betting areas.

Do not infer poker strategy from the robot pose. This guideline describes
physical behavior only.

## Action-Specific Failure Checks

The vision agent may inspect the current action intent, action-sequence
progress, hole-card cache, and previous images to judge whether a failure needs
human help.

Before judging failure or recovery, first decide whether the robot is still in
motion. If the hand is reaching, blurred, lifting a card, moving away from the
table, rotating a card, transporting chips, or otherwise not settled, describe
the action as still in progress. The coding agent should treat that as
`acting` and wait for another capture. Do not call the game failed, do not call
the atom failed, and do not propose `to_recover` while the hand is still
executing the atom.

If the context says a specific step is `dispatched`, explicitly judge whether
that atom appears physically successful, still in progress, retryable, or unsafe
after comparing the current image with the previous state.

Call out a human-help condition when any of these are visible or strongly
suspected:

- During `view_card`, the dexterous hand dropped the card, knocked it out of
  its normal hole-card area, exposed it on the table, or left it in an
  unreadable/unsafe position.
- During `put_down_card`, the returned card overlaps chips, hides chips,
  covers a betting area, covers the turn button, or does not return to the
  expected hole-card area.
- During chip movement, including betting pushes or pulling back winnings, the
  dexterous hand moved a card, button, opponent chip, community card, or any
  non-target object.
- During chip movement, including betting pushes or pulling back winnings, the
  dexterous hand disturbed the unfolded chip layout: chips are scattered,
  denomination groups are mixed, order is no longer countable, or
  inventory/bet chips are no longer separable.
- The dexterous hand appears stuck, pressing into the table, pinning a card or
  chip, or holding an object after the action should have finished.

If the issue is only temporary motion or mild blur, say the robot is still
moving or the scene is unstable rather than immediately requiring human help.
Human help is for physical states that look unsafe to retry or impossible to
parse reliably.

For card-pick/view-card actions, be especially conservative. A card partly
lifted from the table, a card in the gripper but not yet readable, a hand
rotating the card toward the camera, or a hand moving away from the hole-card
area usually means the atom is still running. Do not classify those frames as
missed pickup, failed pickup, dropped card, or lost game unless the hand has
settled and the card is clearly dropped, exposed, misplaced, or pinned.

## Retryable Recovery Checks

Call out a retryable recovery condition when the previous atom action appears
to have failed harmlessly after the hand settled and the table layout is still
intact. These are `to_recover` candidates for the main coding agent:

- During `view_card`, the target card was not picked up and still appears
  face-down near its original hole-card position.
- During `view_card`, the hand missed the card but did not expose, move, cover,
  or damage any game object.
- During chip movement, including betting pushes or pulling back winnings, the
  intended chip did not move or did not follow the dexterous hand, and the chip
  layout remains countable and ordered.
- After a chip-push attempt, no target chip appears to have been pushed, but no
  card, button, chip group, betting area, or opponent object was disturbed.

Only call a state retryable from a settled post-atom view. In workflow terms,
retryable recovery belongs after the scene is stable enough to be
`atom_idle`; it does not belong during `acting`. If the hand is still away from
rest pose, still moving, still holding an object, or the latest two frames show
continued change, the correct visual conclusion is "still in progress; wait",
not `to_recover`.

Also do not call a state retryable if a card is exposed, dropped, misplaced,
hidden, or if chips are scattered, mixed, hidden, or no longer countable. Those
are `down` candidates after the scene has settled because blind retry could
damage the table state.

## Safe Continuation Checks

Say the action looks safe to continue only when:

- no card or chip layout appears damaged,
- target chips/cards are still in recognizable zones,
- no unrelated object was moved,
- any viewed card is either still held for reading or has been returned cleanly,
- the dexterous hand is not stuck or pinning an object.

## Useful Descriptions

Use concise natural language such as:

```text
The dexterous hand is near its initial pose and is not holding a card or chips.
```

```text
The dexterous hand is extended over the table and appears to be holding a card
face-up toward the camera.
```

```text
The dexterous hand is near the chip area and may be pushing chips. The hand is
not near its initial pose.
```

```text
The dexterous hand is still in progress on the card-pick action. It is not near
rest pose, and the card/hand relationship is still changing, so wait for another
capture rather than judging recovery or failure.
```

```text
The dexterous hand appears stuck or pressed against an object; the physical
state is unsafe to continue automatically.
```

```text
Human help needed. During chip movement, the dexterous hand appears to have
scattered the unfolded chip groups, and the denominations are no longer
separable enough for reliable counting.
```

```text
Human help needed. The returned card overlaps a chip group and hides several
chips, so the table state cannot be parsed safely.
```

## Response Contract

Answer in plain language. Include:

- where the dexterous hand is,
- what it appears to be doing,
- whether it is holding a card or chips,
- whether it is near idle/rest pose,
- whether the current action appears safe, still in progress, or failed,
- whether a failure looks retryable without human help,
- any occlusion, disturbed layout, dropped card, moved non-target object, or
  human-help concern.

When the current action is still in progress, say that directly and stop there:
do not also speculate that the atom failed or that recovery is needed. Recovery
and failure labels require a settled post-action image, preferably compared
against at least the previous state and the pre-action state.

Do not produce structured JSON. The coding agent will convert the description
into the `robot` field and use it with `loop_stage`.
