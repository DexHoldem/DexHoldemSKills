# Reviewer perception checks

## Completed reviewer supplement — November 11

[Combined results](results/2026-11-11_reviewer_handoff/RESULTS.md) follow the
original paper's columns: Harness, Perceiver, Overall, LS, TO, BI, CC, CB, RCI,
OCI, SO and Avg. They also report direct scene-stability accuracy, both class
recalls and balanced accuracy for both history conditions.

- **Without annotated history/caches:** all 11 available configurations completed
  36 scenes × 3 repeats = 1,188 trials using the original native paper scripts.
- **With annotated history:** 1,080 original paper outputs cover ten configurations.
  Four GPT 5.6/6 configurations lack their historical raw outputs; a separate
  432-trial annotated supplement supplies their stability predictions. These
  fresh results are explicitly labeled and do not replace the published table.
- **Held-card diagnostic:** the separately reported 11-image experiment includes
  363 calls. It is current-image-only and remains separate from the 36-scene table.

The three unavailable GPT 5.5/5.4/5.4 mini configurations are N/A for the new
ablation, as authorized by the user. No substitute models or zero scores are
used for unavailable services. Both history conditions are fully scored for
all eleven currently accessible configurations.

## Exact input and harness changes

All 593 historical/current JPEGs and all 36 `s_current` links remain unchanged.
The ablation removes only 557 historical `01_parsed_state.md` files, 557 annotated
`02_action.md` files, and 72 `action_sequence.json` / `hole_card_cache.json` files.
Historical images remain available: this is not a current-image-only task.
Original source inputs and saved paper runs are never edited. Previous `runs/`
directories remain excluded by the original isolation process.

The native runner, prompt, guidelines, image-reading tools, output schema,
validity check and deterministic scorer are unchanged. Claude/Gemini source
hashes match their retained paper runs. GPT uses the exact September source
archive and its recorded apps/plugins flags, reasoning effort and service tier.
All 432 paired GPT launch settings match between new conditions apart from
input/output paths and run identifiers. Original source and input hashes were
checked again after completion.

The original Overall definition is unchanged. Avg equally weights the eight
individual field accuracies. Scene stability is read directly from explicit
predictions, never inferred from LS. Labels contain 31 stable and 5 unstable
scenes: always predicting stable gives 86.1% accuracy but 0% unstable recall
and 50% balanced accuracy. The three repeats are not 108 independent scenes.

## Results and evidence

- [Native ablation scores and full raw archive](results/2026-11-10_native_no_annotations/scored_completed/README.md)
- [Original-paper stability rescore](results/2026-11-10_original_stability/README.md)
- [New annotated GPT supplement](results/2026-11-11_annotated_gpt_supplement/README.md)
- [Separate held-card diagnostic](../held_card/README.md)
- [Combined tables](results/2026-11-11_reviewer_handoff/RESULTS.md) and
  [offline audit instructions](results/2026-11-11_reviewer_handoff/REPRODUCE.md)

The shared problem-data ZIP contains the exact ablated inputs, a byte-exact
annotation/cache overlay that restores the original inputs, offline reference
labels, and the separate held-card dataset. The shared results/logs ZIP includes
all raw experiment outputs and attempts, original-control logs, scoring evidence,
source snapshots, and a portable offline audit. ZIP manifests are kept with the
combined report; the large problem-data ZIP is shared through Slack.

## Recovery and interpretation

Claude finished all 540 trials on the user-authorized replacement account.
Gemini 3 Flash recovered exactly eight unanswered/unstarted quota trials through
direct paid Google API authentication using the unchanged original CLI/runner.
All preceding attempts remain archived. Its p29/repeat-3 saved valid answer was
retained despite the later CLI error. Invalid/incorrect answers were not rerun.
The requested Gemini Flash Lite preview alias reports the stable model ID in
all 108 ablation records; it is not claimed identical to the historical preview.

The source/time distinction between historical and newly measured controls is
explicit. Current service aliases, CLI versions and billing routes can differ
from historical runs; these small diagnostics do not establish model rankings
under matched compute. Held-card labels remain proposed_visual_review and the
small red-suit-only subset does not establish general 52-card recognition.

## Validation and superseded work

All 39 CPU-only tests passed. Independent audits verified 1,188 ablation outputs
and 5,808 applicable individual-field scores, 432 fresh annotated outputs and
2,112 field scores, and 1,080 original stability outputs. All ten original table
rows with retained raw data reproduce the paper. Raw archives and ZIP contents
are round-trip hash checked and scanned for credentials.

The earlier tool-free campaign was stopped on the user's protocol correction.
Its retained artifacts remain marked superseded and are excluded from these
results. The initial GPT setup call before locating the archived paper source
was also excluded by configuration before scoring, not by answer quality.
