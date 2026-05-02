# DexHoldem Perception Run

Run: `p5_codex_native_gpt5_5_low_split_batch004_gpt55low_split_low`

Current state: `s3`

## Perception Summary

- `scene_stable`: false
- `is_my_turn`: true
- Held card: unreadable
- Community cards: five visible, all unreadable
- Buttons: dealer and small blind at opponent seat; big blind at robot seat
- Bets: no visible bet chips in my area; one red 5-chip in opponent bet area
- Inventory chips: chip-recognition subagent timed out

## Decision Constraint

The capture should be treated as unstable, so the system should not advance to a robot action from this perception pass.

## Evidence

- Scene stability subagent compared `s2/00_capture.jpg` and `s3/00_capture.jpg` and reported the robot hand was still moving and occluding the lower robot side.
- Turn detection subagent reported that it is our turn.
- Held-card subagent reported a face-down card with no readable face.
- Community-card subagent reported five face-down/unreadable cards.
- Blind-button subagent reported dealer/small blind at the opponent and big blind at the robot.
- Bet-recognition subagent reported one visible red 5-chip in the opponent bet area and no visible chips in my bet area.

## Notes

- No robot action was executed.
- The main agent did not perform image perception directly; only subagent evidence was merged.
