# Evaluation Report

- Current frame is not stable because the robot hand is still moving over the table.
- The workflow remains in `to_recover` based on the failed chip-push recovery context.
- Durable table state carried forward from the prior parsed state:
  - Board: `Qh 7d 6s Jc`
  - Blind: `big_blind`
  - Turn: `true`
  - Chip stacks and bets match the prior parsed state.
- Showdown is not present.
