# Split Visual-Agent Setup

Use the visible split visual agents for image perception.

The main agent must not inspect images or independently decide visual fields.
Delegate each image-reading question to the appropriate scoped visual agent and
merge only returned evidence.

Write one raw evidence file per called subagent under
`runs/<run_id>/visual_raw/<agent_name>.md`.

Then write `runs/<run_id>/visual_summary.json` and
`runs/<run_id>/eval_report.md`. Do not execute robot actions.
