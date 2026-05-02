#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PROBLEM_LIST_FILE="bench/problems/core36_problem_list.txt"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$*"
}

wait_until_reset() {
  local target_epoch
  local now_epoch
  target_epoch="$(python3 - <<'PY'
import datetime
print(int(datetime.datetime(2026, 5, 2, 14, 31, 0).timestamp()))
PY
)"
  now_epoch="$(date +%s)"
  if [ "$now_epoch" -lt "$target_epoch" ]; then
    log "waiting until 2026-05-02 14:31:00 HKT before resuming Claude batches"
    sleep "$((target_epoch - now_epoch))"
  fi
}

run_batch() {
  local label="$1"
  shift
  log "starting ${label}"
  "$@"
  log "finished ${label}"
}

wait_until_reset

run_batch "batch014 claude sonnet 4.6 medium" \
  python3 perception_eval/run_parallel_buffer.py \
    --visual-variant claude_sonnet_4_6_medium \
    --visual-setting split \
    --concurrency 6 \
    --model claude-sonnet-4-6 \
    --reasoning-effort low \
    --agent-max-threads 9 \
    --problem-list-file "$PROBLEM_LIST_FILE" \
    --isolation-root .dexholdem_perception_eval_work \
    --run-prefix batch014_claude_sonnet46medium_split \
    --skip-existing-ok

run_batch "batch015 claude opus 4.7 low" \
  python3 perception_eval/run_parallel_buffer.py \
    --visual-variant claude_opus_4_7_low \
    --visual-setting split \
    --concurrency 6 \
    --model claude-sonnet-4-6 \
    --reasoning-effort low \
    --agent-max-threads 9 \
    --problem-list-file "$PROBLEM_LIST_FILE" \
    --isolation-root .dexholdem_perception_eval_work \
    --run-prefix batch015_claude_opus47low_split \
    --skip-existing-ok

run_batch "batch016 claude opus 4.6 medium" \
  python3 perception_eval/run_parallel_buffer.py \
    --visual-variant claude_opus_4_6_medium \
    --visual-setting split \
    --concurrency 6 \
    --model claude-sonnet-4-6 \
    --reasoning-effort low \
    --agent-max-threads 9 \
    --problem-list-file "$PROBLEM_LIST_FILE" \
    --isolation-root .dexholdem_perception_eval_work \
    --run-prefix batch016_claude_opus46medium_split \
    --skip-existing-ok

run_batch "batch017 claude opus 4.7 medium" \
  python3 perception_eval/run_parallel_buffer.py \
    --visual-variant claude_opus_4_7_medium \
    --visual-setting split \
    --concurrency 6 \
    --model claude-sonnet-4-6 \
    --reasoning-effort low \
    --agent-max-threads 9 \
    --problem-list-file "$PROBLEM_LIST_FILE" \
    --isolation-root .dexholdem_perception_eval_work \
    --run-prefix batch017_claude_opus47medium_split \
    --skip-existing-ok

run_batch "batch018 claude opus 4.7 high" \
  python3 perception_eval/run_parallel_buffer.py \
    --visual-variant claude_opus_4_7_high \
    --visual-setting split \
    --concurrency 6 \
    --model claude-sonnet-4-6 \
    --reasoning-effort low \
    --agent-max-threads 9 \
    --problem-list-file "$PROBLEM_LIST_FILE" \
    --isolation-root .dexholdem_perception_eval_work \
    --run-prefix batch018_claude_opus47high_split \
    --skip-existing-ok

log "all Claude batches finished"
