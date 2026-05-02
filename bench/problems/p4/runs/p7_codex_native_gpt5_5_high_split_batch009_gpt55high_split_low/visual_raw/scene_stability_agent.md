## scene_stability_agent

Status: completed

Unstable. Compared Image #1 previous settled frame with Image #2 current frame. In the current frame, the robot arm is extended into the table area and is holding a visible card near the center-right of the scene, whereas the previous frame had the arm lower/right and not presenting the card. This indicates the cached `view_card left` action is still in progress, not a settled post-action scene.

Uncertainty: the table/chips look otherwise unchanged, but the active robot pose is enough to treat the scene as unstable.
