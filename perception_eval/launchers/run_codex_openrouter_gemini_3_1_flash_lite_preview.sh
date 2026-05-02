#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

exec python3 "$ROOT/perception_eval/run_parallel_buffer.py" \
  --visual-variant "codex_openrouter_gemini_3_1_flash_lite_preview" \
  --visual-setting "${VISUAL_SETTING:-split}" \
  --concurrency "${CONCURRENCY:-6}" \
  --model "${HARNESS_MODEL:-gpt-5.4-mini}" \
  --reasoning-effort "${REASONING_EFFORT:-low}" \
  --service-tier "${SERVICE_TIER:-fast}" \
  --agent-max-threads "${AGENT_MAX_THREADS:-9}" \
  "$@"
