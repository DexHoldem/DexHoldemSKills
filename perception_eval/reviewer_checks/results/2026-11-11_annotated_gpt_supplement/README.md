# New annotated GPT scene-stability supplement

All four available GPT configurations completed 36 scenes × 3 runs (432 trials).
These are new evaluations, run because the original September scene-level logs
are unavailable; they do not replace the published original paper table.

Original historical state/action annotations and both caches are retained, with
all original input bytes checked against frozen hashes. The exact archived paper
GPT script, prompt and settings are reused. All 432 paired launch commands match
the no-annotation arm except input/output locations and run IDs.

[Results and raw archive](scored_completed/README.md) include all original paper
fields plus direct scene stability. [Verification](scored_completed/verification.json)
checks all 432 outputs and 2,112 applicable individual-field scores. Model errors
are retained; there are no accuracy-based retries.
