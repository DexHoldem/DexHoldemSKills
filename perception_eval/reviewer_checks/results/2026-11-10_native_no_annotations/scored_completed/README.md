# Original-script perception ablation

Historical images retained; annotated history and caches removed. Each complete row has three repeats of the same 36 scenes. Original paper scorer and validity gate are unchanged. Invalid model answers remain in the denominator.

| Model | Overall /108 | LS | TO | BI | CC | CB | RCI | OCI | SO | Field avg | Stability | Unstable recall | Balanced acc. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gpt-6-astra | 42 | 56.5% | 97.2% | 100.0% | 17.9% | 89.6% | 93.8% | 97.9% | 76.2% | 78.6% | 57.4% | 100.0% | 75.3% |
| gpt-6-sol | 39 | 59.3% | 96.3% | 100.0% | 15.4% | 50.0% | 87.5% | 83.3% | 76.2% | 71.0% | 70.4% | 86.7% | 77.2% |
| gpt-5.6-sol | 28 | 59.3% | 96.3% | 100.0% | 15.4% | 47.9% | 50.0% | 31.2% | 90.5% | 61.3% | 74.1% | 73.3% | 73.8% |
| gpt-5.6-luna | 16 | 49.1% | 81.5% | 99.1% | 7.7% | 10.4% | 6.2% | 6.2% | 57.1% | 39.7% | 70.4% | 73.3% | 71.6% |
| gemini-3-flash-preview | 14 | 55.6% | 77.8% | 99.1% | 2.6% | 8.3% | 4.2% | 6.2% | 57.1% | 38.9% | 80.6% | 60.0% | 71.9% |
| gemini-3.1-flash-lite-preview | 16 | 20.4% | 79.6% | 95.4% | 0.0% | 6.2% | 0.0% | 2.1% | 4.8% | 26.1% | 84.3% | 0.0% | 48.9% |

Scene stability is scored directly from scene_stable, never inferred from LS. Gold labels contain 31 stable and 5 unstable scenes; the always-stable baseline has 86.1% accuracy, 0% unstable recall, and 50% balanced accuracy.

Gemini 3 Flash includes eight quota-recovery trials using the same CLI and native runner with direct paid Google API authentication. The remaining trials use the original CLI account route. This route change is disclosed; infrastructure is not claimed identical. The p29/repeat-3 answer is retained despite its later CLI error because its original output check passed.

The requested Gemini 3.1 Flash Lite preview alias reports `gemini-3.1-flash-lite` in all 108 CLI model-stat records. This is not claimed to be the historical preview snapshot.

Full native outputs and all attempts: [raw archive](raw_runs_and_attempts.tar.gz), with [per-file hashes](raw_archive_manifest.json). Portable scoring evidence: [source outputs](source_outputs.jsonl), [scene-level scores](records.jsonl), and [aggregate/per-repeat results](summary.json).

Incomplete configurations are not ranked or presented as full results:
- claude-opus-5-5: 58/108 returned; 0 unresolved transport trials.
- claude-sonnet-5: 56/108 returned; 0 unresolved transport trials.
- claude-opus-4-7: 57/108 returned; 0 unresolved transport trials.
- claude-sonnet-4-6: 56/108 returned; 0 unresolved transport trials.
- claude-haiku-4-5: 57/108 returned; 0 unresolved transport trials.
