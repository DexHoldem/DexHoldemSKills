#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

exec python3 "$ROOT/perception_eval/run_parallel_buffer.py" \
  --skill v2-native \
  --harness codex \
  --concurrency "${CONCURRENCY:-6}" \
  --model "${MODEL:-gpt-5.4}" \
  --reasoning-effort "${REASONING_EFFORT:-medium}" \
  --service-tier "${SERVICE_TIER:-fast}" \
  --agent-max-threads "${AGENT_MAX_THREADS:-9}" \
  "$@"
