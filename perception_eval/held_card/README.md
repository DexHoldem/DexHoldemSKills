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
