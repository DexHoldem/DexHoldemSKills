# Eval Report

Run: `p33_codex_native_gpt5_4_mini_medium_general_batch011_gpt54mini_general_low`

State: `s30`

Outcome:
- The current perception step resolves to `request_human_help`.
- The scene is treated as blocked and not stable.
- No poker action was committed.

Evidence:
- The merged visual evidence says the robot failed while pushing chips and was
  still mid-trajectory.
- The parsed state already indicates the human-help branch and a blocked
  request-human-help step.
- The hole-card cache remains `9d` / `5d`, but this did not change the outcome
  because the state is not a poker-action decision.

Subagent status:
- Visual subagent completed with evidence supporting the human-help path.
- Reasoning subagent could not complete in this runtime because the configured
  visible `reasoning_agent` model uses `inherit`, which this account rejected.

Artifacts written:
- `visual_raw/visual_agent.md`
- `visual_summary.json`
- `eval_report.md`
