# Column Benchmarks

These scripts deterministically score perception-run columns against
`bench/problems/ground_truth.json` and `bench/problems/problem_types.json`.
They do not call an LLM judge and they do not parse `eval_report.md`.

Usage:

```bash
perception_eval/column_benchmarks/benchmark_all_columns.sh \
  --batch-dir perception_eval/batch_runs/<batch-id>
```

Each individual table column has a wrapper:

```text
benchmark_overall.sh
benchmark_stage.sh
benchmark_community.sh
benchmark_turn.sh
benchmark_blind.sh
benchmark_bet.sh
benchmark_my_chips.sh
benchmark_opp_chips.sh
benchmark_outcome.sh
benchmark_winner.sh
```

`benchmark_winner.sh` is an alias for `benchmark_outcome.sh`.

Denominators:

```text
Overall: 64
Stage: 64
Turn: 64
Blind: 64
Community: 13 by default, or 36 with --community-scope visible
Bet: 16
My chips: 16
Opp. chips: 16
Outcome/Winner: 7
```

Write detailed outputs:

```bash
perception_eval/column_benchmarks/benchmark_all_columns.sh \
  --batch-dir perception_eval/batch_runs/<batch-id> \
  --out-json /tmp/perception_eval.json \
  --out-csv /tmp/perception_eval.csv
```

Core 36-problem subset:

```bash
perception_eval/column_benchmarks/benchmark_all_columns.sh \
  --batch-dir perception_eval/batch_runs/<batch-id> \
  --problem-list-file bench/problems/core36_problem_list.txt
```

The core subset keeps all table-decision and outcome-judge cases, then trims
repeated robot-progress, recovery, and opponent-wait variants. Its denominators
are Overall/Stage/Turn/Blind 36, Bet/My chips/Opp. chips 16, Community 13 by
default, and Outcome/Winner 7.

The evaluator is strict: missing fields in `visual_summary.json` count as
incorrect. This is intentional for post-schema-change runs; older runs may
score low because their summaries were not canonical.
