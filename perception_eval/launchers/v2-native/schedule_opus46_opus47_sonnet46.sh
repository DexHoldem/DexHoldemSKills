#!/usr/bin/env bash
#
# schedule_opus46_opus47_sonnet46.sh
# ==================================
# Run v2-native perception benchmarks for three Claude models (opus-4.6,
# opus-4.7, sonnet-4.6) across all 36 problems, paced over a 10-hour window.
#
# Motivation
# ----------
# Claude Code enforces a hard 5-hour usage cap that resets at fixed times
# (7:50 AM and 12:50 PM).  Running all 108 jobs (3 models × 36 problems)
# back-to-back would exhaust the budget early and idle until the next reset.
# This script spreads the runs uniformly so token consumption is steady
# across both 5-hour windows.
#
# How it works
# ------------
# - Wraps perception_eval/run_scheduled_models.py.
# - 108 runs are scheduled with ~5 min 33 s between consecutive starts.
# - Round-robin interleaving: opus-4.6 p1 → opus-4.7 p1 → sonnet-4.6 p1 →
#   opus-4.6 p2 → … so that each model's load is evenly distributed.
# - Concurrency 2 (two claude -p processes active at once).  Each run takes
#   ~10 min, so effective throughput ≈ 12 runs/hour → 108 runs in ~9 hours,
#   leaving ~1 hour of slack within the 10-hour window.
# - If a 429 rate-limit response is detected, the scheduler auto-pauses
#   5 minutes before continuing.
# - Runs that already have a passing output_check.json are skipped
#   (--skip-existing-ok), making re-runs safe after partial failures.
# - JSONL event log is written to perception_eval/batch_runs/ for
#   post-hoc analysis.
#
# Usage
# -----
#   # Preview the full 108-run schedule without launching anything:
#   ./schedule_opus46_opus47_sonnet46.sh --dry-run
#
#   # Launch all runs (start at 7:50 AM to align with rate-limit resets):
#   nohup ./schedule_opus46_opus47_sonnet46.sh > schedule.log 2>&1 &
#
#   # Resume after a partial failure (already-done problems are skipped):
#   ./schedule_opus46_opus47_sonnet46.sh
#
#   # Run only a subset of problems:
#   ./schedule_opus46_opus47_sonnet46.sh --problem-start 10 --problem-end 20
#
# Environment variables
# ---------------------
#   DURATION_HOURS     Total pacing window in hours        (default: 10)
#   CONCURRENCY        Max parallel claude -p processes    (default: 2)
#   REASONING_EFFORT   Reasoning effort for claude -p      (default: medium)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$ROOT/perception_eval/batch_runs/schedule_${TIMESTAMP}.jsonl"

exec python3 "$ROOT/perception_eval/run_scheduled_models.py" \
  --models claude-opus-4-6 claude-opus-4-7 claude-sonnet-4-6 \
  --duration-hours "${DURATION_HOURS:-10}" \
  --concurrency "${CONCURRENCY:-2}" \
  --reasoning-effort "${REASONING_EFFORT:-medium}" \
  --skill v2-native \
  --interleave round-robin \
  --skip-existing-ok \
  --log-file "$LOG_FILE" \
  "$@"
