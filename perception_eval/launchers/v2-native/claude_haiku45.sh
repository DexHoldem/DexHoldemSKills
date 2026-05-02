#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

exec python3 "$ROOT/perception_eval/run_parallel_buffer.py" \
  --skill v2-native \
  --harness claude \
  --concurrency "${CONCURRENCY:-6}" \
  --model "${MODEL:-claude-haiku-4-5}" \
  --reasoning-effort "${REASONING_EFFORT:-medium}" \
  --agent-max-threads "${AGENT_MAX_THREADS:-9}" \
  "$@"
