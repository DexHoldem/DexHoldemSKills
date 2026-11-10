# Checking the shared evidence

Open `RESULTS.md` for all paper-column tables and the two-condition stability
comparison. `combined_results.json` keeps machine-readable aggregates and
their independent audit counts. The `with_history` directory contains original
paper outputs; `with_history_new_gpt` contains the explicitly new GPT supplement.
`without_history` retains historical images but removes annotations and caches.

After extracting the **results-and-logs ZIP**, run from its root:

```sh
uv run --no-project python source/reviewer_helpers/audit_reviewer_bundle.py --bundle .
```

This checks all 1,080 original stability trials, 1,188 new ablation trials and
432 new annotated GPT trials from portable raw model outputs, using the exact
original scorer and reference labels bundled under `source/original_native`.
It also independently recomputes all applicable paper fields for both new
campaigns. Expected field checks: 5,808 without history and 2,112 new annotated.
No external model call or GPU is needed for this audit.

`ARCHIVE_MANIFEST.json` contains SHA-256 hashes for every packaged file. Absolute
paths inside raw logs document the execution machine; the offline audit above
does not need those paths to exist. All failed/invalid attempts remain present.

The separate **problem-data ZIP** supplies the ablated inputs, a byte-exact
annotation/cache overlay, and the held-card dataset. Its README and restoration
script explain how to reconstruct the original annotated input tree. Keep
reference labels and result logs outside any model input workspace. The original
runner sources are under `source/original_native`; archived September GPT source
bytes are separately preserved under `source/exact_paper_gpt`.
