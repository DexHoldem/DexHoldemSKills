#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

exec python3 "$ROOT/perception_eval/run_parallel_buffer.py" \
  --skill v2 \
  --visual-variant "claude_haiku_4_5_medium" \
  --visual-setting "${VISUAL_SETTING:-split}" \
  --concurrency "${CONCURRENCY:-6}" \
  --model "${HARNESS_MODEL:-sonnet}" \
  --reasoning-effort "${REASONING_EFFORT:-medium}" \
  --agent-max-threads "${AGENT_MAX_THREADS:-9}" \
  "$@"
