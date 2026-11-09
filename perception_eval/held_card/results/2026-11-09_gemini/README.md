# Gemini held-card recognition — 2026-11-09

2 model configurations, 11 fixed images, 3 independent conversations per image. The 66 completed attempts are repeated measurements of 11 images, not 66 independent scenes.

Label status: **proposed_visual_review**. Scores remain provisional pending human label verification.

## Exact rank-and-suit results

| Model | Repeat 1 | Repeat 2 | Repeat 3 | Mean exact | Mean card macro | Balanced6, per repeat | Invalid JSON | Execution errors |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| Gemini 3 Flash | 7/11 | 8/11 | 9/11 | 72.7% | 72.2% | 5/6, 4/6, 5/6 | 8 | 0 |
| Gemini 3.1 Flash Lite (stable) | 11/11 | 11/11 | 11/11 | 100.0% | 100.0% | 6/6, 6/6, 6/6 | 0 | 0 |

## Per-image correct counts across three repeats

| Image | Gemini 3 Flash | Gemini 3.1 Flash Lite (stable) |
|---|---:|---:|
| hc001 | 3/3 | 3/3 |
| hc002 | 3/3 | 3/3 |
| hc003 | 2/3 | 3/3 |
| hc004 | 2/3 | 3/3 |
| hc005 | 1/3 | 3/3 |
| hc006 | 3/3 | 3/3 |
| hc007 | 3/3 | 3/3 |
| hc008 | 2/3 | 3/3 |
| hc009 | 2/3 | 3/3 |
| hc010 | 2/3 | 3/3 |
| hc011 | 1/3 | 3/3 |

## Interpretation and provenance

- Answers must be a JSON object with exactly `held_card`; prose and code fences are invalid. Invalid answers, abstentions and missing predictions stay in the denominator. Format failures must not be interpreted as pure visual-recognition failures.
- The balanced6 subset contains one image per card identity and is nested within all11. The card macro score weights the six identities equally.
- All selected identities have red suits. Repeated recording contexts, no empty-hand or unreadable negatives, and small sample size limit generalization and ranking claims.
- This is a new image-only diagnostic, separate from the original 36-problem history-conditioned table. The original table and manuscript are unchanged.
- Model IDs, protocol and content hashes are in [manifest.json](manifest.json); per-repeat and per-card scores are in [summary.json](summary.json). [responses.jsonl](responses.jsonl) preserves each original final response and execution status. Complete CLI streams remain in the local campaign directory.
- Execution status counts: `{"completed": 58, "invalid_answer": 8}`.
- Validation: 13 dataset/scoring and input/extraction tests passed.

## Model version difference

The requested `gemini-3.1-flash-lite-preview` ID returned `gemini-3.1-flash-lite` in every Flash-Lite call. This result is labeled as the current stable model; it does not reproduce the retired preview used in the original paper. See [Google's deprecation notice](https://ai.google.dev/gemini-api/docs/deprecations).

The raw campaign initially rejected these responses as model mismatches. A separate offline derivation revalidates them against the actual stable ID, retaining requested IDs and original validation status. No response was rerun, selected by correctness, or changed; the strict answer parser is identical.
