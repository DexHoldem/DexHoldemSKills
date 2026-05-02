# General Visual-Agent Setup

Use the single visible visual agent for image perception.
Use the visible reasoning agent for Texas Hold'em poker-action reasoning when
the router asks for `choose_poker_action`.

The main agent must not inspect images or independently decide visual fields.
Delegate image-reading questions to the visual agent and merge only its
returned evidence.

Write raw evidence to `runs/<run_id>/visual_raw/visual_agent.md`.

Then write `runs/<run_id>/visual_summary.json` and
`runs/<run_id>/eval_report.md`. Do not execute robot actions.
