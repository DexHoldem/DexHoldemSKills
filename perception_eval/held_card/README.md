# Held-card image-only evaluation

This runner evaluates the five Claude configurations in the DexHoldem paper on
the separate `held_card_image_only_v1` package. It is a recognition diagnostic,
not a rerun of the original 36-problem perception benchmark. The source package
and its original evaluator remain unchanged.

## Protocol

- Models: `claude-opus-5-5`, `claude-sonnet-5`, `claude-opus-4-7`,
  `claude-sonnet-4-6`, and `claude-haiku-4-5`.
- All models request `medium` effort through Claude Code. Three fresh
  conversations per image; 11 images per model, 165 conversations in total.
- Each request contains exactly the sample's neutral question and unchanged JPEG
  bytes, sent as a multimodal user message. No preprocessing, cropping, history,
  source filename, question ID, answer vocabulary restriction, or label is added.
  Any internal image transformation by the service is outside this runner.
- Every call has an empty temporary working directory, no available tools, no MCP
  servers, no persistent session, and Claude safe mode. Labels and scoring run
  only in the parent process. The response's tool list and resolved model ID are
  checked; fallback to a different model is not accepted.
- This dedicated input protocol differs from the original filesystem-based
  perception harness. The new scores must not be substituted into that table.
- Each response is parsed as a whole JSON document with exactly `held_card`.
  Prose and Markdown fences are not searched for an answer. Invalid answers,
  missing predictions and abstentions remain incorrect under the package scorer.
  Infrastructure errors are additionally identified in `execution_errors`.
- Existing case records are reused on resume, including failures. There is no
  correctness-based retry or best-of selection. A manifest prevents resuming
  after dataset, label, scorer, runner, model or repeat-count changes.
- The initial one-image Opus connectivity pilot is excluded from formal scores.

## Run

From outside the source-data directory:

```sh
uv run --no-project python perception_eval/held_card/run_claude.py \
  --dataset /path/to/held_card_image_only_v1 \
  --output /path/to/results/claude_medium_r3 \
  --concurrency 2
```

`--summarize-only` reconstructs summaries from saved case records. Dataset labels
are needed only for scoring; they are never placed in the model's working
directory or input message.

Each case retains `stdout.jsonl`, `stderr.txt`, and `record.json`. Per model and
repeat, `predictions.jsonl` and `scores.json` contain predictions and both
`all11` and `balanced6` metrics. `summary.json` collects the five models without
treating repeats as independent images. `manifest.json` records input, label,
scorer and runner hashes, and `claude_version.txt` records the CLI version.

## Validation and limits

Existing dataset tests cover input image integrity, unique images, grouping,
input allowlists, balanced coverage, score denominators and abstention. The new
tests cover exact multimodal input construction, exclusion of labels/source
paths, strict response extraction, model substitution and unexpected tools.

```sh
uv run --no-project --with pytest python -m pytest -q \
  perception_eval/held_card/test_run_claude.py
```

The dataset's gold labels are marked `proposed_visual_review`; accuracy is
provisional until the labels are verified by a person. There are 11 images,
six card identities, and only red suits, with repeated cards and recording
contexts. `balanced6` is a nested one-image-per-identity diagnostic, not an
independent test set. Report per-repeat counts and macro accuracy over the six
identities, and do not claim general 52-card recognition or a stable ranking
from this small subset.

## Gemini extension

`run_gemini.py` evaluates the two Gemini IDs from the main paper:
`gemini-3-flash-preview` and `gemini-3.1-flash-lite-preview`. It uses the same
11 unchanged images, neutral question, three repeats, frozen labels, original
scorer, strict JSON extraction, and separate balanced6 reporting. No reasoning
override is supplied, consistent with the original Gemini launchers.

Gemini CLI receives an `@image.jpg` attachment from a fresh temporary directory.
Only the selected image and a restrictive settings file are present there;
neither history nor private labels are copied. Core tools, MCP servers, hooks,
extensions and normal context-file loading are disabled. The CLI's attachment
preprocessor supplies the image before inference; model tool calls must remain
zero and the reported model must match exactly. Gemini's CLI prompt wrapper and
service-side image handling differ from Claude's; equal inference compute is
not claimed. Full stdout/stderr and actual model/token statistics are saved.

```sh
uv run --no-project python perception_eval/held_card/run_gemini.py \
  --dataset /path/to/held_card_image_only_v1 \
  --output /path/to/results/gemini_r3 --concurrency 2

uv run --no-project python perception_eval/held_card/resolve_gemini_alias.py \
  /path/to/held_card_image_only_v1 \
  /path/to/results/gemini_r3 \
  /path/to/results/gemini_resolved_r3

uv run --no-project python perception_eval/held_card/report.py \
  /path/to/results/gemini_resolved_r3 \
  perception_eval/held_card/results/2026-11-09_gemini
```

The live service resolved the retired `gemini-3.1-flash-lite-preview` ID to
`gemini-3.1-flash-lite` in all 33 calls. The source runner correctly rejected
that identity mismatch. `resolve_gemini_alias.py` creates a separate derived
campaign labeled as the actual stable model, retaining original request IDs,
validation status and raw responses; it makes no additional inference calls.
This is not a reproduction of the paper's retired preview. The alias resolution
is supported by [Google's deprecation notice](https://ai.google.dev/gemini-api/docs/deprecations).

The one-image Flash connectivity pilot is excluded from formal scores. Four
additional tests in `test_run_gemini.py` check the Gemini output envelope,
strict formatting, abstention, execution errors, model substitution and tool
use. Two more tests cover the explicit retired-to-stable identity derivation
and rejection of other substitutions. Together with the three shared
input/extraction tests and four original dataset tests, all 13 checks pass.

## Codex extension

`run_codex.py` accepts the seven exact GPT IDs from the paper. On 2026-11-09,
connectivity preflights succeeded for `gpt-6-astra`, `gpt-6-sol`, `gpt-5.6-sol`,
and `gpt-5.6-luna`; the formal campaign evaluates those four configurations,
11 images × 3 independent repeats each (132 responses), at medium effort and
fast service tier. `gpt-5.5`, `gpt-5.4`, and `gpt-5.4-mini` returned HTTP 400
`model_not_found` with this ChatGPT account. They have no score and are not
replaced by newer models. All connectivity pilot responses are excluded.

Codex CLI receives the unchanged JPEG through `--image` and the unchanged
neutral question on stdin. Each call has a fresh temporary directory containing
only `image.jpg`, uses an ephemeral session and a read-only sandbox, ignores
user configuration and rules, disables document loading and host skill discovery,
and disables shell, apps/plugins, multi-agent, memory, hooks, web search and image
inspection/generation features. Labels remain in the parent evaluator. Any
observed tool invocation, API error, metadata fallback or dropped service-tier
warning invalidates the attempt. No structured-output schema is imposed; the
same strict whole-response JSON parser and frozen scorer apply.

Codex JSONL does not independently expose backend model identity. Records retain
the exact requested ID and leave `resolved_models` empty; successful acceptance
of an ID is not represented as independent backend attestation. The CLI's system
prompt and image handling also differ from Claude/Gemini, so these are CLI-based
measurements with matched task inputs, not equal-compute API comparisons.

```sh
uv run --no-project python perception_eval/held_card/run_codex.py \
  --dataset /path/to/held_card_image_only_v1 \
  --output /path/to/results/codex_medium_r3 \
  --models gpt-6-astra gpt-6-sol gpt-5.6-sol gpt-5.6-luna \
  --concurrency 3

uv run --no-project python perception_eval/held_card/report.py \
  /path/to/results/codex_medium_r3 \
  perception_eval/held_card/results/2026-11-09_codex
```

The five Codex checks cover strict answers, abstention, failed/incomplete turns,
tool events, configuration warnings and the command's input isolation. Together
with the existing nine runner/alias tests and four frozen-package tests,
18 tests pass. Labels remain `proposed_visual_review`; results are provisional.

The first Codex extractor mistook a progress message followed by a final answer
for an execution error. `reparse_codex.py` derives a separate campaign from the
unchanged JSONL streams, selecting the last assistant message as the final
response (matching the other CLI final-response envelopes). It retains all
assistant messages, original statuses, original records and source hashes.
The final message must still parse as strict JSON; earlier messages are never
searched for a valid answer. There are no additional inference calls or
correctness-based retries. The raw campaign retains its original runner source.

```sh
uv run --no-project python perception_eval/held_card/reparse_codex.py \
  /path/to/held_card_image_only_v1 \
  /path/to/results/codex_medium_r3 \
  /path/to/results/codex_final_response_r3
```
