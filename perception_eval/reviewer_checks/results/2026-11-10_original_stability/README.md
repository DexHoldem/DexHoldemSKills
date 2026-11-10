# Scene-stability rescoring of original perception runs — 2026-11-10

Same annotated-history outputs as the selected paper batches. No new inference. Each model has three repeats of 36 scenes, not 108 independent scenes.

Gold: 31 stable and 5 unstable scenes. Always-stable baseline: 31/36 (86.1%) overall, 0/5 unstable recall, and 50.0% balanced accuracy.

| Model | Per-repeat correct /36 | Stable /93 | Unstable /15 | Accuracy | Balanced accuracy | Missing/invalid | Original Overall /108 | Overall + stability /108 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| GPT 5.5 | 29, 29, 29 | 72 | 15 | 80.6% | 88.7% | 0 | 34 | 34 |
| GPT 5.4 | 28, 29, 26 | 68 | 15 | 76.9% | 86.6% | 0 | 34 | 34 |
| GPT 5.4 mini | 25, 23, 28 | 65 | 11 | 70.4% | 71.6% | 0 | 28 | 28 |
| Opus 5.5 | 29, 30, 31 | 75 | 15 | 83.3% | 90.3% | 0 | 53 | 52 |
| Sonnet 5 | 28, 30, 29 | 72 | 15 | 80.6% | 88.7% | 0 | 39 | 39 |
| Opus 4.7 | 25, 25, 27 | 64 | 13 | 71.3% | 77.7% | 0 | 37 | 35 |
| Sonnet 4.6 | 31, 31, 30 | 77 | 15 | 85.2% | 91.4% | 0 | 27 | 27 |
| Haiku 4.5 | 32, 29, 30 | 82 | 9 | 84.3% | 74.1% | 0 | 15 | 15 |
| Gemini 3 Flash | 27, 28, 26 | 67 | 14 | 75.0% | 82.7% | 0 | 22 | 21 |
| Gemini 3.1 Flash L. | 30, 29, 30 | 89 | 0 | 82.4% | 47.8% | 3 | 11 | 3 |

Stability is scored directly from saved scene_stable fields, never inferred from LS. Original Overall remains unchanged; the additional column is a separate, stricter diagnostic. No held-card field is added to this aggregate. Missing and invalid outputs remain in denominators.

Per-problem predictions and source hashes: [records.jsonl](records.jsonl). Per-repeat scores and confusion counts: [summary.json](summary.json). Exact batch selection and provenance: [manifest.json](manifest.json).
