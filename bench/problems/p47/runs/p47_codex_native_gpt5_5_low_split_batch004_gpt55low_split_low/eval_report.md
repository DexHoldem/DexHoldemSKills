# Eval Report

## Outcome

Perception step completed with merged visual evidence only.

## Evidence Summary

- `held_card_recognition_agent`: no robot-held card visible; unreadable.
- `community_cards_agent`: five community cards visible, read as `Qs Qh 7d Qc 7c`.
- `blind_button_recognition_agent`: dealer/small blind on opponent side, big blind on robot side.
- `turn_detection_agent`: it is our turn.
- `scene_stability_agent`: unstable; robot hand/camera still in motion.
- `chip_recognition_agent`: approximate inventory counts returned for both sides.
- `reasoning_agent`: failed to run because the inherited model is unsupported in this account.

## Assessment

The visual evidence supports that the table state is readable, but the scene is not stable enough to advance a robot action step. No robot actions were executed.
