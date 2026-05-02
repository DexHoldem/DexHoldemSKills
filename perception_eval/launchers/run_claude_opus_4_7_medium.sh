#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

exec python3 "$ROOT/perception_eval/run_parallel_buffer.py" \
  --visual-variant "claude_opus_4_7_medium" \
  --visual-setting "${VISUAL_SETTING:-split}" \
  --concurrency "${CONCURRENCY:-6}" \
  --model "${HARNESS_MODEL:-claude-sonnet-4-6}" \
  --reasoning-effort "${REASONING_EFFORT:-low}" \
  --agent-max-threads "${AGENT_MAX_THREADS:-9}" \
  "$@"
