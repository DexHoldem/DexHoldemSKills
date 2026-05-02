# chip_recognition_agent

Best-effort inventory read, excluding bets/pot/buttons/cards:

- Robot/player side: red `4`, blue `4`, green `0`, brown `0`
- Opponent side: red `2`, blue `4`, green `0`, brown `0`

Uncertainty:

- Top-side blue cluster is partly crowded; could be off by `±1` chip.
- Bottom-side red cluster is partly occluded by the board edge/camera arm; could be off by `±1` chip.
- White/purple special chips were not counted because they are not one of the requested denominations.
