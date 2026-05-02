# Perception Step Report

Run: `p58_codex_native_gpt5_4_mini_medium_split_batch003_gpt54mini_split_low`

## Merged Evidence

- Scene is stable enough to continue from the current frame.
- Turn button is visible and indicates it is our turn.
- Dealer button is at the robot seat; robot is small blind and opponent is big blind.
- Community cards read as `Jh Ac Ks 4c Kd`.
- Best-estimate current bets:
  - Opponent: red 4, blue 2, green 2, brown 0
  - Robot: red 3, blue 3, green 0, brown 4
- Inventory estimates:
  - Robot: red 3, blue 5, green 0, brown 3
  - Opponent: red 4, blue 5, green 0, brown 3
- Robot-held card is unreadable from the visible frame.
- Robot arm is present on the right side and appears to be hovering/positioning, but no unsafe contact or active failure is visible.
- Showdown appears visible, but the outcome is not fully reliable from the current frame alone because the opponent hole cards are not fully readable and the board read has minor uncertainty.

## Conclusion

The current perception step supports a stable, our-turn showdown-visible state with readable board cards and unresolved outcome certainty. No robot action was executed.
