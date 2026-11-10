> **Superseded:** This changed-harness diagnostic is excluded from the requested paper-history ablation. The corrected run reuses the original paper scripts and removes annotated inputs only.

# Paired annotated-history ablation — gpt-6-astra, 2026-11-10

Fresh matched tool-free runs: 36 scenes × 3 trial repetitions × 2 conditions. Both conditions receive every historical image through the current frame, the same native field guidelines, and the same structured-output task. The ablated condition removes all prior parsed states, action_sequence.json (including prior LS), and hole_card_cache.json (including blind cache). This tests removal of all annotated prior context, not just parsed states.

The direct-image harness differs from the historical native-agent harness. Compare the two fresh conditions with each other; do not subtract their scores from the published table. All trials use requested model gpt-6-astra, codex CLI, effort: medium; service tier: fast. Tools are disabled and each trial starts a fresh session. No score-based retries. No-answer service failures may be retried with the earlier attempt preserved under attempts/. Quota-recovery events, if any, are recorded separately.

| Condition | Overall | Field average | LS | TO | BI | CC | CB | RCI | OCI | SO | Stability | Stable recall | Unstable recall | Balanced stability | Overall + stability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| annotated | 48.1% | 82.5% | 71.3% | 97.2% | 100.0% | 17.9% | 93.8% | 93.8% | 100.0% | 85.7% | 68.5% | 63.4% | 100.0% | 81.7% | 45.4% |
| images_only_history | 37.0% | 80.0% | 61.1% | 97.2% | 100.0% | 12.8% | 89.6% | 93.8% | 100.0% | 85.7% | 61.1% | 54.8% | 100.0% | 77.4% | 37.0% |

Field denominators per repeat: LS 36, TO 36, BI 36, CC 13, CB 16, RCI 16, OCI 16, SO 7. Field average is the unweighted mean of the eight field accuracies. Original Overall uses the original per-problem relevant-column conjunction; stability is added only in the separate extended score.

| Condition | Repeat Overall /36 | Repeat stability /36 | History scenes Overall | No-history scenes Overall | Status counts |
|---|---|---|---|---|---|
| annotated | 18, 17, 17 | 25, 24, 25 | 30/72 | 22/36 | {'completed': 108} |
| images_only_history | 13, 13, 14 | 22, 22, 22 | 18/72 | 22/36 | {'completed': 108} |

All scenes: ablated minus annotated Overall = -11.1 percentage points; descriptive paired scene-cluster bootstrap 95% interval [-22.2, -2.8] pp. Pair counts: {'both_correct': 39, 'both_wrong': 55, 'annotated_only': 13, 'ablated_only': 1}. Repeated attempts are clustered by scene, not treated as independent scenes.

Scenes with image history: ablated minus annotated Overall = -16.7 percentage points; descriptive paired scene-cluster bootstrap 95% interval [-33.3, -4.2] pp. Pair counts: {'both_correct': 18, 'both_wrong': 42, 'annotated_only': 12}. Repeated attempts are clustered by scene, not treated as independent scenes.

Stability labels: 31 stable / 5 unstable. Always-stable baseline: 86.1% accuracy, 0% unstable recall, 50% balanced accuracy. Missing or invalid responses remain errors in all applicable denominators.

This small diagnostic does not establish a model ranking. It does not add held-card identity to the 36-scene score; the separate 11-image held-card diagnostic remains a distinct experiment.

Scoring mode: single_outer_code_fence_removed. Outer code fences removed in 0 responses. The formatting diagnostic accepts only a single fenced JSON object with no surrounding prose; it never selects between multiple answers, changes field values, or repairs malformed JSON. Provider/model/tool validity checks remain identical.

Audit artifacts: [manifest](manifest.json), [summary](summary_fence_normalized.json), [scene-level scores](scores_fence_normalized.jsonl), frozen prompts under inputs/, and unmodified CLI events plus parsed records under trials/.

Model identity evidence is the requested CLI ID; Codex JSONL does not attest the backend ID.
