# DexHoldem Perception Step

Current state: `s38`

Result:
- Scene stability: unstable
- Turn status: it is our turn
- Community cards: `Qs`, `8h`, `7d`, `6s`, `Jc?`

Decision:
- No robot action was executed.
- The latest frame is not settled enough for a follow-up action because the robot arm/gripper is still over the newly placed facedown card stack.

Evidence:
- [`visual_raw/scene_stability.txt`](visual_raw/scene_stability.txt)
- [`visual_raw/turn_detection.txt`](visual_raw/turn_detection.txt)
- [`visual_raw/community_cards.txt`](visual_raw/community_cards.txt)
