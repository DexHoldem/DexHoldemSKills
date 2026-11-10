# DexHoldem perception reviewer supplement

Status: All 11 accessible configurations complete: 1,188 native ablation trials, plus 432 new annotated GPT trials for missing scene-stability evidence. Each configuration/condition uses 36 scenes × 3 runs.

## What changed

**Without annotated history / cached information:** keep the original native paper script, prompt, guidelines, image-reading tools, output schema, validity check and deterministic scorer. Remove only historical parsed-state annotations, annotated action notes, action_sequence.json and hole_card_cache.json. Retain every historical/current image and s_current link. This is not current-image-only evaluation and is not autonomous history prediction.

**With annotated history:** score the existing scene_stable predictions retrospectively for the ten configurations with retained paper logs. For GPT 6 Astra/6 Sol/5.6 Sol/5.6 Luna, whose old scene-level logs are unavailable, run 36 × 3 new annotated trials with the exact original paper script and original input bytes. These four fresh results are explicitly distinguished from historical runs and never substituted for the published paper table. The original Overall/field metrics below are copied from the exact paper table, and all ten configurations with available old raw outputs are independently reproduced.

Each configuration averages three runs on the same 36 scenes. They are not 108 independent scenes. Column denominators per run are Overall/LS/TO/BI 36, CC 13, CB/RCI/OCI 16, SO 7. Avg equally weights the eight field accuracies and excludes Overall. Invalid model output remains wrong; no best-of or correctness-based reruns.

## Original paper: with annotated history (%)

| Harness | Perceiver | Overall | LS | TO | BI | CC | CB | RCI | OCI | SO | Avg |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex | GPT 6 Astra | 48.1 | 69.4 | 97.2 | 100.0 | 20.5 | 93.8 | 93.8 | 100.0 | 66.7 | 80.2 |
| Codex | GPT 6 Sol | 46.3 | 66.7 | 96.3 | 98.1 | 43.6 | 79.2 | 91.7 | 83.3 | 76.2 | 79.4 |
| Codex | GPT 5.6 Sol | 46.3 | 78.7 | 95.4 | 100.0 | 38.5 | 68.8 | 75.0 | 56.2 | 85.7 | 74.8 |
| Codex | GPT 5.6 Luna | 27.8 | 62.0 | 79.6 | 97.2 | 43.6 | 41.7 | 47.9 | 50.0 | 57.1 | 59.9 |
| Codex | GPT 5.5 | 31.5 | 72.2 | 80.6 | 100.0 | 61.5 | 45.8 | 62.5 | 35.4 | 76.2 | 66.8 |
| Codex | GPT 5.4 | 31.5 | 65.7 | 93.5 | 100.0 | 23.1 | 31.2 | 56.2 | 18.8 | 47.6 | 54.5 |
| Codex | GPT 5.4 mini | 25.9 | 56.5 | 94.4 | 99.1 | 33.3 | 14.6 | 29.2 | 18.8 | 47.6 | 49.2 |
| Claude Code | Opus 5.5 | 49.1 | 76.9 | 97.2 | 100.0 | 20.5 | 81.2 | 91.7 | 91.7 | 85.7 | 80.6 |
| Claude Code | Sonnet 5 | 36.1 | 61.1 | 94.4 | 100.0 | 5.1 | 31.2 | 33.3 | 35.4 | 23.8 | 48.1 |
| Claude Code | Opus 4.7 | 34.3 | 43.5 | 93.5 | 100.0 | 43.6 | 31.2 | 37.5 | 43.8 | 0.0 | 49.1 |
| Claude Code | Sonnet 4.6 | 25.0 | 46.3 | 88.0 | 100.0 | 23.1 | 10.4 | 29.2 | 22.9 | 14.3 | 41.8 |
| Claude Code | Haiku 4.5 | 13.9 | 47.2 | 68.5 | 91.7 | 35.9 | 12.5 | 25.0 | 18.8 | 0.0 | 37.4 |
| Gemini CLI | Gemini 3 Flash | 20.4 | 63.9 | 77.8 | 100.0 | 28.2 | 18.8 | 29.2 | 22.9 | 71.4 | 51.5 |
| Gemini CLI | Gemini 3.1 Flash L. | 10.2 | 27.8 | 73.1 | 94.4 | 28.2 | 12.5 | 22.9 | 14.6 | 0.0 | 34.2 |

## New annotated GPT supplement (%) — separate from the original paper

These four fresh runs supply the missing WITH-history scene-stability predictions. Full original columns are retained for transparency; these are not the published historical results.

| Harness | Perceiver | Overall | LS | TO | BI | CC | CB | RCI | OCI | SO | Avg |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex | GPT 6 Astra | 43.5 | 61.1 | 97.2 | 100.0 | 20.5 | 93.8 | 93.8 | 100.0 | 71.4 | 79.7 |
| Codex | GPT 6 Sol | 39.8 | 63.9 | 96.3 | 100.0 | 30.8 | 81.2 | 91.7 | 87.5 | 66.7 | 77.3 |
| Codex | GPT 5.6 Sol | 49.1 | 77.8 | 97.2 | 100.0 | 43.6 | 77.1 | 72.9 | 56.2 | 90.5 | 76.9 |
| Codex | GPT 5.6 Luna | 28.7 | 63.0 | 80.6 | 96.3 | 38.5 | 37.5 | 35.4 | 45.8 | 52.4 | 56.2 |

## New ablation: without annotated history / cached information (%)

| Harness | Perceiver | Overall | LS | TO | BI | CC | CB | RCI | OCI | SO | Avg |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex | GPT 6 Astra | 38.9 | 56.5 | 97.2 | 100.0 | 17.9 | 89.6 | 93.8 | 97.9 | 76.2 | 78.6 |
| Codex | GPT 6 Sol | 36.1 | 59.3 | 96.3 | 100.0 | 15.4 | 50.0 | 87.5 | 83.3 | 76.2 | 71.0 |
| Codex | GPT 5.6 Sol | 25.9 | 59.3 | 96.3 | 100.0 | 15.4 | 47.9 | 50.0 | 31.2 | 90.5 | 61.3 |
| Codex | GPT 5.6 Luna | 14.8 | 49.1 | 81.5 | 99.1 | 7.7 | 10.4 | 6.2 | 6.2 | 57.1 | 39.7 |
| Codex | GPT 5.5 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Codex | GPT 5.4 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Codex | GPT 5.4 mini | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Claude Code | Opus 5.5 | 36.1 | 68.5 | 97.2 | 100.0 | 28.2 | 43.8 | 77.1 | 87.5 | 76.2 | 72.3 |
| Claude Code | Sonnet 5 | 21.3 | 51.9 | 95.4 | 100.0 | 7.7 | 6.2 | 2.1 | 6.2 | 42.9 | 39.0 |
| Claude Code | Opus 4.7 | 20.4 | 25.0 | 96.3 | 96.3 | 7.7 | 2.1 | 4.2 | 2.1 | 28.6 | 32.8 |
| Claude Code | Sonnet 4.6 | 13.9 | 19.4 | 82.4 | 98.1 | 5.1 | 2.1 | 4.2 | 0.0 | 38.1 | 31.2 |
| Claude Code | Haiku 4.5 | 4.6 | 21.3 | 74.1 | 46.3 | 0.0 | 4.2 | 6.2 | 6.2 | 0.0 | 19.8 |
| Gemini CLI | Gemini 3 Flash | 13.0 | 55.6 | 77.8 | 99.1 | 2.6 | 8.3 | 4.2 | 6.2 | 57.1 | 38.9 |
| Gemini CLI | Gemini 3.1 Flash L. | 14.8 | 20.4 | 79.6 | 95.4 | 0.0 | 6.2 | 0.0 | 2.1 | 4.8 | 26.1 |

N/A for GPT 5.5/5.4/5.4 mini means the retired model IDs were unavailable, not zero accuracy. No substitute model was used.

## Scene-stability comparison (%)

The score reads `table.scene_stable` directly, never infers stability from LS. Labels: 31 stable and 5 unstable scenes per run. Always-stable baseline: **86.1% accuracy, 100% stable recall, 0% unstable recall, 50% balanced accuracy**. Balanced accuracy averages the two class recalls. The original Overall definition remains unchanged.

| Perceiver | History info | Accuracy | Stable recall | Unstable recall | Balanced accuracy | Missing/invalid /108 |
|---|---|---:|---:|---:|---:|---:|
| GPT 6 Astra | With (new supplement) | 60.2 | 53.8 | 100.0 | 76.9 | 0 |
| GPT 6 Astra | Without | 57.4 | 50.5 | 100.0 | 75.3 | 0 |
| GPT 6 Sol | With (new supplement) | 69.4 | 64.5 | 100.0 | 82.3 | 0 |
| GPT 6 Sol | Without | 70.4 | 67.7 | 86.7 | 77.2 | 0 |
| GPT 5.6 Sol | With (new supplement) | 81.5 | 78.5 | 100.0 | 89.2 | 0 |
| GPT 5.6 Sol | Without | 74.1 | 74.2 | 73.3 | 73.8 | 0 |
| GPT 5.6 Luna | With (new supplement) | 75.0 | 71.0 | 100.0 | 85.5 | 0 |
| GPT 5.6 Luna | Without | 70.4 | 69.9 | 73.3 | 71.6 | 0 |
| GPT 5.5 | With (original paper) | 80.6 | 77.4 | 100.0 | 88.7 | 0 |
| GPT 5.5 | Without | N/A | N/A | N/A | N/A | N/A |
| GPT 5.4 | With (original paper) | 76.9 | 73.1 | 100.0 | 86.6 | 0 |
| GPT 5.4 | Without | N/A | N/A | N/A | N/A | N/A |
| GPT 5.4 mini | With (original paper) | 70.4 | 69.9 | 73.3 | 71.6 | 0 |
| GPT 5.4 mini | Without | N/A | N/A | N/A | N/A | N/A |
| Opus 5.5 | With (original paper) | 83.3 | 80.6 | 100.0 | 90.3 | 0 |
| Opus 5.5 | Without | 83.3 | 83.9 | 80.0 | 81.9 | 0 |
| Sonnet 5 | With (original paper) | 80.6 | 77.4 | 100.0 | 88.7 | 0 |
| Sonnet 5 | Without | 88.9 | 92.5 | 66.7 | 79.6 | 0 |
| Opus 4.7 | With (original paper) | 71.3 | 68.8 | 86.7 | 77.7 | 0 |
| Opus 4.7 | Without | 76.9 | 83.9 | 33.3 | 58.6 | 0 |
| Sonnet 4.6 | With (original paper) | 85.2 | 82.8 | 100.0 | 91.4 | 0 |
| Sonnet 4.6 | Without | 81.5 | 93.5 | 6.7 | 50.1 | 0 |
| Haiku 4.5 | With (original paper) | 84.3 | 88.2 | 60.0 | 74.1 | 0 |
| Haiku 4.5 | Without | 80.6 | 93.5 | 0.0 | 46.8 | 6 |
| Gemini 3 Flash | With (original paper) | 75.0 | 72.0 | 93.3 | 82.7 | 0 |
| Gemini 3 Flash | Without | 80.6 | 83.9 | 60.0 | 71.9 | 1 |
| Gemini 3.1 Flash L. | With (original paper) | 82.4 | 95.7 | 0.0 | 47.8 | 3 |
| Gemini 3.1 Flash L. | Without | 84.3 | 97.8 | 0.0 | 48.9 | 3 |

WITH-history GPT 6 Astra/6 Sol/5.6 Sol/5.6 Luna values are NEW original-script evaluations because their historical scene-level logs are unavailable. All other WITH-history values use original paper outputs. Their published aggregate scores cannot recover scene stability. The superseded tool-free experiment is excluded entirely. WITHOUT-history N/A for the three retired GPT IDs is an availability limit. Both settings are directly scored for all eleven accessible configurations; the source/time distinction is explicit.

## Separate image-only held-card diagnostic

This previously shared diagnostic contains 11 images × 3 runs × 11 configurations = 363 calls. It supplies only the current image and a neutral prompt, with no history or labels. It is a distinct rank-and-suit task, not a replacement for the original perception table.

| Model | Correct /33 | Exact (%) | Card macro (%) | Balanced6 repeats /6 |
|---|---:|---:|---:|---|
| Opus 5.5 | 32 | 97.0 | 97.2 | 6, 6, 5 |
| Sonnet 5 | 33 | 100.0 | 100.0 | 6, 6, 6 |
| Opus 4.7 | 33 | 100.0 | 100.0 | 6, 6, 6 |
| Sonnet 4.6 | 30 | 90.9 | 91.7 | 6, 6, 6 |
| Haiku 4.5 | 0 | 0.0 | 0.0 | 0, 0, 0 |
| Gemini 3 Flash | 24 | 72.7 | 72.2 | 5, 4, 5 |
| Gemini 3.1 Flash Lite (stable) | 33 | 100.0 | 100.0 | 6, 6, 6 |
| GPT 6 Astra | 33 | 100.0 | 100.0 | 6, 6, 6 |
| GPT 6 Sol | 30 | 90.9 | 91.7 | 5, 5, 5 |
| GPT 5.6 Sol | 27 | 81.8 | 83.3 | 5, 5, 5 |
| GPT 5.6 Luna | 23 | 69.7 | 69.4 | 3, 4, 4 |

Held-card labels remain proposed_visual_review; human verification is required. All 11 images show red suits, with only six card identities. Haiku's 0/33 reflects invalid output format and must not be described as zero visual ability. The preserved strict parser also rejects correct answers inside Markdown fences. No model ranking or general 52-card claim is supported by this small diagnostic.

## Provenance and interpretation

- Gemini 3 Flash: eight unanswered/unstarted quota trials were recovered using the unchanged original Gemini CLI with direct paid Google API authentication. All previous attempts are preserved; all eight returned the requested model ID. The original p29/repeat-3 answer remains despite its later CLI error because output_check passed. Invalid answers were not rerun.
- Gemini 3.1 Flash Lite: the requested preview alias resolves to stable gemini-3.1-flash-lite in all 108 ablation records; it is not claimed identical to the historical preview snapshot.
- Model service snapshots, CLI versions and billing routes may differ from the original runs. These comparisons are descriptive diagnostics, not an isolated causal estimate or a ranking under matched compute.
- Scene-stability accuracy measures a predicted scene_stable field; it does not by itself measure downstream wait/continue/recover decisions or physical scene-preserving execution.
- The problem-data ZIP separates the ablated input tree, the removed annotation/cache overlay, offline gold labels, and the held-card dataset. The logs/results ZIP contains raw outputs and attempts, portable scoring evidence, exact paper table source, and reproduction scripts. Never place offline labels or result logs in a model's input workspace.
