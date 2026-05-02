# Scene Stability Agent — s20/00_capture.jpg

**Verdict: UNSTABLE**

## Visual Evidence

**Robot arm position — major change, still active:**
In s19 the robot arm was in a mid-reach posture over the central table. In s20 the arm has moved substantially closer to the camera; the large cylindrical actuator body dominates the lower-right foreground and the gripper is positioned low and forward over the chip area. This is a large positional change consistent with an ongoing chip-push action.

**Table occlusion increased:**
The robot body in s20 occludes a much larger portion of the lower-center table than in s19. The chip layout in the robot betting zone and robot inventory zone is substantially obscured. The "Your Turn" button and chips visible in s19's lower-left region are now partially blocked.

**Chip layout change visible:**
The chip grouping in the central/robot betting area appears to have shifted between s19 and s20, but full confirmation is blocked by the robot arm occlusion.

**No settled idle pose:**
The robot arm has not returned to a near-idle, retracted, or resting position. It is still extended over the table in an active-action posture.

## Prior State Context
s19 noted: "robot acting pushing chips 10, wait" with scene_stable=false. Visual evidence in s20 is fully consistent with that action still in progress or having just completed a movement segment not yet resolved to a settled state.

## Recommendation
**Wait and recapture.** Do not proceed with a poker decision or new robot movement from this frame.
