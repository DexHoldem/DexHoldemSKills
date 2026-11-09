# Claude held-card recognition — 2026-11-09

Five paper models, 11 fixed images, three independent conversations per image. The 165 completed attempts are repeated measurements of 11 images, not 165 independent scenes.

Label status: **proposed_visual_review**. Scores remain provisional pending human label verification.

## Exact rank-and-suit results

| Model | Repeat 1 | Repeat 2 | Repeat 3 | Mean exact | Mean card macro | Balanced6, per repeat | Invalid JSON | Execution errors |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| Opus 5.5 | 11/11 | 11/11 | 10/11 | 97.0% | 97.2% | 6/6, 6/6, 5/6 | 1 | 0 |
| Sonnet 5 | 11/11 | 11/11 | 11/11 | 100.0% | 100.0% | 6/6, 6/6, 6/6 | 0 | 0 |
| Opus 4.7 | 11/11 | 11/11 | 11/11 | 100.0% | 100.0% | 6/6, 6/6, 6/6 | 0 | 0 |
| Sonnet 4.6 | 10/11 | 10/11 | 10/11 | 90.9% | 91.7% | 6/6, 6/6, 6/6 | 0 | 0 |
| Haiku 4.5 | 0/11 | 0/11 | 0/11 | 0.0% | 0.0% | 0/6, 0/6, 0/6 | 33 | 0 |

## Per-image correct counts across three repeats

| Image | Opus 5.5 | Sonnet 5 | Opus 4.7 | Sonnet 4.6 | Haiku 4.5 |
|---|---:|---:|---:|---:|---:|
| hc001 | 2/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc002 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc003 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc004 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc005 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc006 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc007 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc008 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc009 | 3/3 | 3/3 | 3/3 | 0/3 | 0/3 |
| hc010 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| hc011 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |

## Interpretation and provenance

- Answers must be a JSON object with exactly `held_card`; prose and code fences are invalid. Invalid answers, abstentions and missing predictions stay in the denominator. Format failures must not be interpreted as pure visual-recognition failures.
- The balanced6 subset contains one image per card identity and is nested within all11. The card macro score weights the six identities equally.
- All selected identities have red suits. Repeated recording contexts, no empty-hand or unreadable negatives, and small sample size limit generalization and ranking claims.
- This is a new image-only diagnostic, separate from the original 36-problem history-conditioned table. The original table and manuscript are unchanged.
- Model IDs, protocol and content hashes are in [manifest.json](manifest.json); per-repeat and per-card scores are in [summary.json](summary.json). [responses.jsonl](responses.jsonl) preserves each original final response and execution status. Complete CLI streams remain in the local campaign directory.
- Execution status counts: `{"completed": 131, "invalid_answer": 34}`.
- Validation: four existing dataset/scoring tests and three new input/extraction tests passed.
