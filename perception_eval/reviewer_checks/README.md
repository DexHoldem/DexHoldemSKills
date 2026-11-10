# Reviewer perception checks

## Corrected paper-script ablation (active)

The user requested the original paper scripts with historical annotations and
caches removed. `native_ablation.py` now invokes those original single-run
scripts directly. It does not replace the prompt, image-reading tools, output
schema, output validation or scoring functions. Published annotated-history
results are the control; no new annotated-control runs are scheduled.

All 593 historical/current images across 36 problem folders remain byte-identical,
as do the 36 `s_current` links. Independent copies omit only the 557
`01_parsed_state.md` files, 557 `02_action.md` files and 72 cache files
(`action_sequence.json` and `hole_card_cache.json`). Action notes are annotated
context too: their prose explicitly states visual/robot states. Original source
inputs and saved runs are never modified. Prior `runs/` directories are excluded
as in the original harness.

Each of 11 available configurations has 36 problems × 3 repeats = 108 planned
trials. The three inaccessible GPT 5.5/5.4/5.4 mini configurations remain N/A,
as authorized by the user. Model aliases and current CLI versions are recorded;
a current service alias is not evidence of the same historical model snapshot.

Claude/Gemini source hashes match their retained paper runs. GPT 5.6/6 use the
September paper source archive and its recorded apps/plugins flags. The archive's
Windows CRLF bytes were restored and all recorded source hashes verified.
The [frozen protocol](results/2026-11-10_native_no_annotations/protocol.json)
records the retained/removed inputs; the [GPT provenance](results/2026-11-10_native_no_annotations/gpt_paper_provenance.json)
records the original source and command settings. Runtime/OS versions are
recorded separately and are not claimed to reproduce historical infrastructure.

Working results are under `/private/tmp/dexholdem_native_ablation` while the
campaign runs. GPT and Gemini each passed their first formal p3 trial's original
output checks, and their full queues are active. These formal trials are reused.
Claude is scheduled for 2026-11-11 02:51 Asia/Singapore after its quota reset.
Completed/malformed answers are retained without score-based retries; explicit
zero-token Claude quota errors preserve all attempts and defer until the next
provider-stated reset. Unknown failures remain visible for inspection.

Original `evaluate_column.py` remains authoritative for Overall and field scores.
Direct `table.scene_stable` scoring is added separately to the same outputs;
it does not alter the original Overall. Full results are pending.

## Completed retrospective stability scoring

[Original-run stability](results/2026-11-10_original_stability/README.md) covers
10 original model configurations × 108 retained predictions = 1,080 trials.
No new inference was needed. The original validity gate and field evaluator
are reused, and `audit_original.py` verifies the portable raw-output archive.
Four September GPT model run folders were unavailable, so their historical
stability values are not imputed from aggregate paper scores.

The 36 labels contain 31 stable and 5 unstable scenes. Report accuracy, both
class recalls and balanced accuracy. The always-stable baseline is 86.1%
accuracy, 0% unstable recall and 50% balanced accuracy. Invalid predictions
remain in the original denominators. Extended Overall requires original Overall
and correct stability, and is reported separately.

## Superseded tool-free diagnostics

The earlier direct-image/tool-free paired campaign changed the original harness.
It was stopped on the user's correction, including the old Claude resume timer.
Its Astra and partial all-model artifacts remain under their original result
folders with `SUPERSEDED.json` markers. They must not be relabeled or used as
the requested original-script ablation. Source scripts are retained to explain
those historical artifacts, not as the current execution route.

The initial GPT native setup call before locating the September source archive
was also excluded by configuration before scoring, with its evidence retained
under `excluded_setup_check/`. No answer-quality selection was performed.

The separate [11-image held-card diagnostic](../held_card/README.md) is unchanged
and remains a distinct experiment.

## Validation

Run CPU-only tests from a temporary directory with `uv run --no-project python
-m pytest`. Current tests cover input removal, unchanged images/links, original
runner commands, quota-only retry gates, stability scoring and archive auditing.
All 32 relevant tests passed at this checkpoint. No local GPU scripts are used.
