# Reviewer-check implementation

## Retrospective stability scoring

`evaluate_stability.py` consumes an explicit three-batch selection for each
model and the original `evaluate_column.py` validity gate. It reads stability
only from explicit prediction fields; LS is never used as a proxy. Boolean and
true/false string values are accepted; conflicting aliases or missing values
are invalid. Invalid predictions remain in both class and overall denominators.

The original Overall is recomputed with the unchanged reference evaluator.
Extended Overall is its conjunction with correct stability. Neither modifies
the original definition or adds held-card identity. Each trial retains source
hashes. `audit_original.py` rederives every score from the portable raw-summary
and output-check archive without requiring the original ignored run folders.

## Superseded matched annotation ablation

`history_ablation.py` constructs both conditions from an allowlist: all `sN`
images through `s_current`, prior `01_parsed_state.md` files only, and the two
explicit context caches. Current/future annotations, gold labels, prior run
outputs, arbitrary files and symlinked external target directories are excluded.
All actual model images are copied into fresh temporary workspaces. Prior
text is embedded only in the annotated condition; no tools are enabled.

Prompts, image hashes and the runner hash are frozen before inference. Resume
requires an identical manifest and CLI version. Each trial is a new ephemeral
Codex process. Condition submission order alternates by problem and repetition.
The first two smoke-check trials are retained in the planned 216-trial sample;
no trial is rerun because of its answer. Every raw event stream, stderr stream,
parsed record, model setting and input hash is retained.

`score_history.py` runs after completion. It checks trial identity, input
hashes and agreement of parsed answers with raw final responses, then uses the
original column definitions with `community_scope=high`. It reports the eight
field accuracies, their macro-average, original Overall, direct stability,
and extended Overall. Historical-image and single-image strata are separate.
Paired Overall uncertainty resamples scenes with all their repeats together
(10,000 resamples; fixed seed); it does not treat 108 attempts as 108 scenes.

The direct-image harness intentionally controls all input delivery between the
two new conditions. It is not a reproduction of the older tool-using native
agent runs. Differences from the published table cannot isolate history effects.
This experiment removes all annotated prior context, including workflow cache,
not just the previous parsed state.

## Provider expansion and failures

`providers.py` transports the identical chronological image files and frozen
prompt to Claude (base64 image blocks) or Gemini (`@frame` attachments), with
tools and external context disabled. Provider usage metadata checks the actual
model IDs. The known Gemini Flash Lite alias is explicitly recorded as a stable
model. `multi_campaign.py` first checks access and the longest input (43 frames),
then schedules the available models. Probe answers are excluded from scores.
Three unavailable GPT IDs remain N/A after explicit access errors, as authorized
by the user; they are never replaced by another model or counted as zero scores.

Each family has a bounded worker pool. A transient service error with no answer
can receive one retry, preserving its original artifacts under `attempts/`.
Quota exhaustion stops scheduling new calls for that model. Astra's 20 quota
failures before the account upgrade were separately preserved and recovered
after the upgrade. No incorrect or invalid-format answer is rerun by score.

`score_history.py --normalize-fences` produces a separate diagnostic without
altering strict scores or raw records. Only one whole-response Markdown fence
around a JSON object can be removed. Multiple objects, prose and malformed JSON
remain invalid. `summarize_campaign.py` checks identical cross-model input
manifests and requires every available model's 216 records before writing a
final consolidated report; unavailable and incomplete models are distinct.

## Verification

The existing original column evaluator is reused rather than replaced.
The new tests cover stability aliases and conflicts, absent fields, class
imbalance, missing-prediction denominators, temporal input selection,
annotation exclusion, disabled tools, final-message parsing, unequal field
denominators, and scene-level pairing. A separate archive audit checks the
1,080 original predictions against original scoring functions and source hashes.

## Corrected native ablation

The corrected controller does not implement model inference: it invokes the
original paper runner scripts, which retain their prompts, image-reading tools,
preflight, raw evidence outputs, and output checks. Dataset preparation removes
only annotated state/action text and the two context caches; images, state
ordering and current-image links are hashed and verified. Original dataset/run
files are never edited. Historical GPT source assets and startup flags come
from the paper provenance archive, with exact historical hashes restored.
Claude and Gemini runners match their saved original run hashes.

The former tool-free queue and timed Claude continuation were stopped on the
user's correction. Their raw artifacts remain, marked superseded. No existing
result is relabeled as having used the native harness. New tests verify input
exclusion, byte-identical images, preserved links, original runner invocation,
and zero-token quota-only recovery. No answer-quality retry is allowed.

## Rolling queue update

The bounded queue refills each completed request without a whole-batch barrier.
GPT/Claude/Gemini now use 6/6/4 workers. Old controllers drained existing calls
before replacements acquired the provider locks; 119 preexisting record hashes
were verified unchanged. Only scheduling changed: frozen model inputs, original
inference scripts, prompts, tools and scoring remain unchanged. Quota or wrapper
errors stop new submissions and drain ongoing requests. Real-thread tests cover
refill, concurrency bounds, exactly-once results and safe stopping. All 35
relevant tests passed. Throughput comparisons across different scenes are
descriptive only; later scenes may take substantially longer.

## Paid Google API recovery and completed-model export — 2026-11-11

Gemini 3 Flash exhausted the original CLI account quota near the end of repeat 3.
Three unanswered 429 trials (p26–p28) and five unstarted trials (p32–p36) are
recovered using direct paid Gemini Developer API authentication. The original
Gemini CLI, native runner, prompt, tool permissions, images and output checks
are unchanged. This authentication/backend route change is explicit in every
recovered record; it is not claimed identical to the original service route.
OpenRouter connectivity checks failed before any benchmark recovery request.

`recover_gemini_google.py` acquires the existing provider lock, verifies frozen
source/input hashes, and validates an explicit eight-trial plan before launch.
It requires both a missing answer and explicit 429/RESOURCE_EXHAUSTED evidence
to retry a failed trial. Invalid or answered trials are never selected. The p29
repeat-3 answer is retained despite its later CLI error because the original
output check passed. Old canonical failure records and attempt artifacts are
preserved. Hashes of all unaffected Gemini records are verified after recovery.
The two-worker rolling queue stops new submissions on a transport/wrapper error.
Run-local authentication settings and the credential are kept outside the repo.

`score_native.py` uses the original column evaluator and its default `high`
community-card scope. It exports Overall, all eight paper fields, field average,
and explicit stable/unstable metrics for configurations with all 108 returned
trials and no unresolved transport failures. Invalid model outputs remain in
the denominators. Incomplete Claude configurations are listed separately.
The portable summary/output-check archive is independently checked using
`audit_original.py`; raw runner outputs and all attempts are also retained.
There are 36 distinct scenes repeated three times, not 108 independent scenes.

The existing tests cover input preservation, original runner arguments, quota
handling, rolling queues and stability scoring. Three new real-filesystem
tests cover recovery eligibility and rejection of answered, invalid-output and
non-quota cases. The selected 19 tests pass. No credentials are committed.
