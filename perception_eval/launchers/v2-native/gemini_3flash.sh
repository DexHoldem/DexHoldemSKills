#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

exec python3 "$ROOT/perception_eval/run_parallel_buffer.py" \
  --skill v2-native \
  --harness gemini \
  --concurrency "${CONCURRENCY:-6}" \
  --model "${MODEL:-gemini-3-flash-preview}" \
  --reasoning-effort "${REASONING_EFFORT:-not_supported}" \
  --agent-max-threads "${AGENT_MAX_THREADS:-9}" \
  "$@"
