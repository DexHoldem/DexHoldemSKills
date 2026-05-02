#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_PREFIX="${RUN_PREFIX:-core36_gpt54mini_split_low_$(date +%Y%m%d_%H%M%S)}"

CONCURRENCY="${CONCURRENCY:-6}" \
HARNESS_MODEL="${HARNESS_MODEL:-gpt-5.4-mini}" \
REASONING_EFFORT="${REASONING_EFFORT:-low}" \
SERVICE_TIER="${SERVICE_TIER:-fast}" \
exec "$ROOT/perception_eval/launchers/run_codex_native_gpt5_4_mini_medium.sh" \
  --problem-list-file "$ROOT/bench/problems/core36_problem_list.txt" \
  --run-prefix "$RUN_PREFIX" \
  --skip-existing-ok \
  --allow-failures \
  "$@"
