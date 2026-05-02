# Eval Report

Current perception step was completed with a conservative merge of the visible subagent evidence.

## Outcome

- Scene stability: unstable
- Loop stage: acting
- Turn: our turn
- Recommended action: wait

## Key Evidence

- The scene stability agent reported the robot arm was still sweeping across the table and that the frame was not stable enough for the next decision.
- The robot behavior agent said the hand was extended over the betting area after a raise attempt and did not appear unsafe, but it was not fully at rest.
- The turn-detection agent reported `Your Turn`.
- The reasoning agent recommended `wait` because the scene was still unstable.

## Merged Visual Read

- Community cards were only partially reliable from the current frame, so the summary keeps the first card uncertain.
- Betting-area and inventory chip counts were not perfectly aligned across agents, so the summary preserves uncertainty instead of overfitting one read.

## Notes

- No robot actions were executed.
- The main agent did not perform image perception directly; the result was assembled from subagent evidence only.
