# New annotated GPT supplement

New annotated GPT scene-stability supplement using the original paper scripts and all original historical annotations/caches. Does not replace published paper results. Each complete row has three repeats of the same 36 scenes. Original paper scorer and validity gate are unchanged. Invalid model answers remain in the denominator.

| Model | Overall /108 | LS | TO | BI | CC | CB | RCI | OCI | SO | Field avg | Stability | Unstable recall | Balanced acc. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gpt-6-astra | 47 | 61.1% | 97.2% | 100.0% | 20.5% | 93.8% | 93.8% | 100.0% | 71.4% | 79.7% | 60.2% | 100.0% | 76.9% |
| gpt-6-sol | 43 | 63.9% | 96.3% | 100.0% | 30.8% | 81.2% | 91.7% | 87.5% | 66.7% | 77.3% | 69.4% | 100.0% | 82.3% |
| gpt-5.6-sol | 53 | 77.8% | 97.2% | 100.0% | 43.6% | 77.1% | 72.9% | 56.2% | 90.5% | 76.9% | 81.5% | 100.0% | 89.2% |
| gpt-5.6-luna | 31 | 63.0% | 80.6% | 96.3% | 38.5% | 37.5% | 35.4% | 45.8% | 52.4% | 56.2% | 75.0% | 100.0% | 85.5% |

Scene stability is scored directly from scene_stable, never inferred from LS. Gold labels contain 31 stable and 5 unstable scenes; the always-stable baseline has 86.1% accuracy, 0% unstable recall, and 50% balanced accuracy.



Full native outputs and all attempts: [raw archive](raw_runs_and_attempts.tar.gz), with [per-file hashes](raw_archive_manifest.json). Portable scoring evidence: [source outputs](source_outputs.jsonl), [scene-level scores](records.jsonl), and [aggregate/per-repeat results](summary.json).

All declared configurations are complete.
