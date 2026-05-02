# DexHoldem Perception Report

- State: `s3`
- Scene stability: unstable
- Turn: our turn
- Community cards: 4 visible, all unreadable
- Held card: no readable held card visible
- Blind button: not safely identifiable
- Bets: not safely identifiable
- Chip inventory: partially readable, with some occlusion

## Summary

The scene is not stable enough to advance the perception loop. The white turn button indicates it is our turn, but the table image still shows motion/change between `s2` and `s3`, so this step should be treated as a wait-and-recapture condition rather than an action commit.

## Evidence

- Scene stability agent reported the foreground robot arm/camera moved between `s2/00_capture.jpg` and `s3/00_capture.jpg`.
- Turn detection agent reported the white "Your Turn" button near the bottom-left robot seat.
- Community card agent reported four visible cards, all face-down/unreadable.
- Held-card agent reported no readable held card visible.
- Blind-button and bet-recognition agents reported the relevant fields were not safely identifiable.

## Notes

No robot action was executed.
