# Codex held-card recognition — 2026-11-09

4 model configurations, 11 fixed images, 3 independent conversations per image. The 132 completed attempts are repeated measurements of 11 images, not 132 independent scenes.

Label status: **proposed_visual_review**. Scores remain provisional pending human label verification.

## Exact rank-and-suit results

| Model | Repeat 1 | Repeat 2 | Repeat 3 | Mean exact | Mean card macro | Balanced6, per repeat | Invalid JSON | Execution errors |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| GPT 6 Astra | 11/11 | 11/11 | 11/11 | 100.0% | 100.0% | 6/6, 6/6, 6/6 | 0 | 0 |
| GPT 6 Sol | 10/11 | 10/11 | 10/11 | 90.9% | 91.7% | 5/6, 5/6, 5/6 | 0 | 0 |
| GPT 5.6 Sol | 9/11 | 9/11 | 9/11 | 81.8% | 83.3% | 5/6, 5/6, 5/6 | 0 | 0 |
| GPT 5.6 Luna | 7/11 | 8/11 | 8/11 | 69.7% | 69.4% | 3/6, 4/6, 4/6 | 0 | 0 |

## Per-image correct counts across three repeats

| Image | GPT 6 Astra | GPT 6 Sol | GPT 5.6 Sol | GPT 5.6 Luna |
|---|---:|---:|---:|---:|
| hc001 | 3/3 | 3/3 | 3/3 | 3/3 |
| hc002 | 3/3 | 3/3 | 3/3 | 3/3 |
| hc003 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc004 | 3/3 | 3/3 | 3/3 | 2/3 |
| hc005 | 3/3 | 3/3 | 3/3 | 3/3 |
| hc006 | 3/3 | 0/3 | 0/3 | 0/3 |
| hc007 | 3/3 | 3/3 | 3/3 | 3/3 |
| hc008 | 3/3 | 3/3 | 3/3 | 3/3 |
| hc009 | 3/3 | 3/3 | 0/3 | 0/3 |
| hc010 | 3/3 | 3/3 | 3/3 | 3/3 |
| hc011 | 3/3 | 3/3 | 3/3 | 3/3 |

## Interpretation and provenance

- Answers must be a JSON object with exactly `held_card`; prose and code fences are invalid. Invalid answers, abstentions and missing predictions stay in the denominator. Format failures must not be interpreted as pure visual-recognition failures.
- The balanced6 subset contains one image per card identity and is nested within all11. The card macro score weights the six identities equally.
- All selected identities have red suits. Repeated recording contexts, no empty-hand or unreadable negatives, and small sample size limit generalization and ranking claims.
- This is a new image-only diagnostic, separate from the original 36-problem history-conditioned table. The original table and manuscript are unchanged.
- Model IDs, protocol and content hashes are in [manifest.json](manifest.json); per-repeat and per-card scores are in [summary.json](summary.json). [responses.jsonl](responses.jsonl) preserves each original final response and execution status. Complete CLI streams remain in the local campaign directory.
- Execution status counts: `{"completed": 132}`.
- Validation: 18 dataset/scoring and input/extraction tests passed.

## Codex identity and availability

These are the exact model IDs requested through Codex CLI. Its JSONL events do not expose an independent backend model ID; `resolved_models` is therefore empty rather than inferred. API errors, observed tool invocations, fallback metadata warnings and dropped service-tier warnings are rejected.

Separate connectivity checks are preserved in [availability.json](availability.json). All preflight predictions, including successful calls, are excluded from formal scores.

Original-paper IDs unavailable in this account: `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.5`. These configurations were not replaced and have no recognition score. The service errors are retained in the availability record.

The initial extractor incorrectly classified multiple assistant messages as execution failures. A separate offline derivation parses the final assistant message, consistently with the other CLI final-response envelopes. Earlier commentary is retained in `assistant_messages`; the final message must still be strict JSON. Source records, original statuses and hashes are retained. No inference was repeated or selected by correctness.
