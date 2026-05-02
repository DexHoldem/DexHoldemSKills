# Perception Step Report

Current state: `s0`

Merged visual result:
- Scene stability: unstable
- Turn ownership: not our turn
- Community cards: `Kh`, `3s`, `3c`, `5h`, `Tc`
- Dealer / blinds: dealer `robot`, small blind `robot`, big blind `opponent`
- Robot current bet: `1x blue 10`, `1x brown 100`
- Opponent current bet: no definite chips visible in the upper betting lane
- Robot inventory: `5x red 5`, `5x blue 10`, `0x green 50`, `2x brown 100`
- Opponent inventory: `5x red 5`, `5x blue 10`, `0x green 50`, `3x brown 100`

Confidence notes:
- Scene stability is conservative because only one frame was available and the robot arm/camera is still extended over the table.
- Opponent bet and opponent brown-chip inventory are partially occluded, so those counts are the least certain fields.

Router-facing interpretation:
- This frame should be treated as a visual parse result, not an action step.
- Because the scene is unstable, the safe follow-up is to wait rather than advance the embodied sequence.

No robot actions were executed.
