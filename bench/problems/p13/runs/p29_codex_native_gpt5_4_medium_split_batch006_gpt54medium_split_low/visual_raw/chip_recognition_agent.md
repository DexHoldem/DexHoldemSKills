# chip_recognition_agent

From the image alone, counting only visible remaining inventory chips and excluding bet/pot/button chips:

Robot/player inventory visible:
- Red `5`: 4
- Blue `10`: 3
- Green `50`: 4
- Brown `100`: 0 visible

Opponent inventory visible:
- Red `5`: 2
- Blue `10`: about 6 visible
- Green `50`: about 2 visible
- Brown `100`: about 3 visible

Uncertain / not countable:
- Opponent right-side cluster near seat `1` is partially crowded and partly occluded by the robot hand/camera; the split between blue/green/brown there is approximate.
- Opponent blue-chip cluster left of center is overlapping; counted as visible faces only, but exact total could be off by 1.
- Mid-table chips near the community cards and the two chips near the lower-left card area were treated as non-inventory/bet-area chips and excluded.
