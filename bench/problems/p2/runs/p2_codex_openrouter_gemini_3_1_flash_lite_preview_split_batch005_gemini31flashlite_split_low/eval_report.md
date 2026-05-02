# Eval Report

Perception step could not be completed in this runtime because the required named visual subagents were unavailable.

What I verified:
- The current state is `s0`.
- The sequence is `idle`.
- No robot action was executed.

What blocked completion:
- The runtime rejected each named visual subagent request with `agent type is currently not available`.
- I did not replace subagent evidence with main-agent image inspection.

Outputs written:
- `visual_raw/README.md`
- `visual_summary.json`
- `eval_report.md`
