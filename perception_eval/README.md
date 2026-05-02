# Perception Evaluation

Benchmark harness for evaluating visual perception in DexHoldem poker agents.

## Skills

Two skill modes are supported:

- **v2** (dexholdem-v2): Uses visual subagents for perception. The harness model
  delegates image analysis to specialized subagents.
- **v2-native** (dexholdem-v2-native): No subagents. The harness model performs
  perception directly.

## Experiment Matrix

### dexholdem-v2 (with subagents)

| Harness | Harness Model | Perceiver (subagent) |
|---------|---------------|----------------------|
| Codex | gpt-5.4-mini | codex_native_gpt5_4_mini_medium |
| Codex | gpt-5.4-mini | codex_native_gpt5_4_medium |
| Codex | gpt-5.4-mini | codex_native_gpt5_5_medium |
| Claude | sonnet | claude_sonnet_4_6_medium |
| Claude | sonnet | claude_opus_4_6_medium |
| Claude | sonnet | claude_opus_4_7_medium |
| Claude | sonnet | claude_haiku_4_5_medium |

### dexholdem-v2-native (no subagents)

| Harness | Model (does perception directly) |
|---------|----------------------------------|
| Codex | gpt-5.4-mini |
| Codex | gpt-5.4 |
| Codex | gpt-5.5 |
| Claude | sonnet |
| Claude | opus |
| Claude | haiku |

## Launchers

Batch launchers are organized by skill:

```text
launchers/
  v2/                           # dexholdem-v2 with subagents
    codex_perceiver_gpt54mini.sh
    codex_perceiver_gpt54medium.sh
    codex_perceiver_gpt55medium.sh
    claude_perceiver_sonnet46.sh
    claude_perceiver_opus46.sh
    claude_perceiver_opus47.sh
    claude_perceiver_haiku45.sh
  v2-native/                    # dexholdem-v2-native without subagents
    codex_gpt54mini.sh
    codex_gpt54medium.sh
    codex_gpt55medium.sh
    claude_sonnet46.sh
    claude_opus46.sh
    claude_opus47.sh
    claude_haiku45.sh
```

## Preflight

Use the preflight script to set up a benchmark problem:

```bash
# v2 with subagents
python3 perception_eval/preflight.py \
  --problem-dir bench/problems/p3 \
  --skill v2 \
  --visual-setting split \
  --visual-variant codex_native_gpt5_4_mini_medium \
  --run-id p3_test_001

# v2-native without subagents
python3 perception_eval/preflight.py \
  --problem-dir bench/problems/p3 \
  --skill v2-native \
  --harness codex \
  --run-id p3_native_test_001
```

List available variants:

```bash
python3 perception_eval/preflight.py --list
```

## Single-Run Wrappers

### Codex

```bash
python3 perception_eval/run_codex_benchmark.py \
  --problem-dir bench/problems/p3 \
  --skill v2 \
  --visual-setting split \
  --visual-variant codex_native_gpt5_4_mini_medium \
  --run-id p3_codex_split_001 \
  --model gpt-5.4-mini \
  --reasoning-effort medium
```

For native mode:

```bash
python3 perception_eval/run_codex_benchmark.py \
  --problem-dir bench/problems/p3 \
  --skill v2-native \
  --run-id p3_codex_native_001 \
  --model gpt-5.4-mini \
  --reasoning-effort medium
```

### Claude

```bash
python3 perception_eval/run_claude_benchmark.py \
  --problem-dir bench/problems/p3 \
  --skill v2 \
  --visual-setting split \
  --visual-variant claude_sonnet_4_6_medium \
  --run-id p3_claude_split_001 \
  --model sonnet \
  --reasoning-effort medium
```

## Parallel Batch Runs

Use the parallel buffer engine for batch evaluation:

```bash
# v2 with subagents
python3 perception_eval/run_parallel_buffer.py \
  --skill v2 \
  --visual-variant codex_native_gpt5_4_mini_medium \
  --visual-setting split \
  --concurrency 6 \
  --model gpt-5.4-mini \
  --reasoning-effort medium

# v2-native without subagents
python3 perception_eval/run_parallel_buffer.py \
  --skill v2-native \
  --harness codex \
  --concurrency 6 \
  --model gpt-5.4-mini \
  --reasoning-effort medium
```

Or use the convenience launchers:

```bash
# v2 with subagents
perception_eval/launchers/v2/codex_perceiver_gpt54mini.sh

# v2-native without subagents
perception_eval/launchers/v2-native/codex_gpt54mini.sh
```

Defaults:
- problems: p1 through p36
- concurrency: 6 active subprocesses
- visual setting: split (v2 only)
- reasoning effort: medium

Override defaults with env vars:

```bash
CONCURRENCY=8 REASONING_EFFORT=high \
  perception_eval/launchers/v2/codex_perceiver_gpt54mini.sh \
  --problem-list p1,p2,p3 --dry-run
```
