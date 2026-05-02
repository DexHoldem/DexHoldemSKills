# chip_recognition_agent

Opponent inventory, top side:
- `red=2`, `blue=4`, `green=2`, `brown=3`
- Zones counted: top-left cluster in the `6` box (`2 red`), top-center-left cluster beside the cards (`4 blue`), top-right cluster in/near the `1` box (`2 green`, `3 brown`)
- Uncertainty: top-right cluster is slightly crowded but all five visible faces appear countable

Robot/player inventory, bottom side:
- `red=4`, `blue=3`, `green=0`, `brown=0`
- Zones counted: bottom-left cluster around the `6` box and beside the hole card (`4 red`, `3 blue`)
- Uncertainty: none in that bottom-left inventory zone

Not countable / excluded:
- Chips near the middle betting line on the lower half (`1 green, 1 blue, 2 brown`) look like committed bet chips, not remaining inventory
- Chips near the robot gripper on the bottom-right are heavily occluded; denomination/count cannot be read reliably, so I am not including them as inventory
- Dealer/button discs and all pot/bet chips are excluded
