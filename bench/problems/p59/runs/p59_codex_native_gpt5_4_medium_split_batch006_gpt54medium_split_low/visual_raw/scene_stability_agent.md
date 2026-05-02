Unstable. Compared `s0/00_capture.jpg` only.

Concrete visual reason: a large robot arm/end-effector is extended over the table and occludes a meaningful portion of the right side of the scene, including parts of cards/chips/seat areas. That indicates the scene is still in progress or at least not fully settled for reliable perception. There is no obvious full-frame motion blur, but the heavy foreground occlusion is enough to make the frame unreliable.

Visible reliability issues:
- Robot hardware blocks a substantial right-side field of view.
- Some table objects on the right are partially hidden by the arm/device.
- No prior frame was provided, so I cannot confirm whether the arm is moving or just parked.

Confidence: high that this frame is not stable enough for the current perception step because of active occlusion; medium on any stronger claim about motion since only one image was provided.
