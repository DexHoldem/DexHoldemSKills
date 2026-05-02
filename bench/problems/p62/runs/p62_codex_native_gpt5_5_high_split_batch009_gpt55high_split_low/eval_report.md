# Eval Report

Run ID:
- `p62_codex_native_gpt5_5_high_split_batch009_gpt55high_split_low`

Summary:
- The scene is not stable enough for a fully trusted perception state because the robot end-effector is still extended over the table.
- It is our turn.
- Board cards visible: `4c` (low-confidence suit), `As`, `Jh`.
- Blind/button assignment: dealer and small blind are the opponent; big blind is the robot.
- Robot-held hole card is not readable in the frame.
- Inventory chips were estimated from the visible seat bands with some occlusion uncertainty.

Reasoning:
- No poker-action decision was committed.
- Because the user requested a perception step and not robot execution, I merged only visual subagent evidence into the report.

Notes:
- The current frame contains enough evidence to identify turn status and visible board cards, but not enough to safely read a robot-held card.
