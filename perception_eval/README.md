# Perception Evaluation Preflight

Use one dynamic preflight script to expose a requested visual-agent setting
inside a benchmark problem folder:

```bash
python3 perception_eval/preflight.py \
  --problem-dir bench/problems/p3 \
  --visual-setting split \
  --visual-variant codex_native_gpt5_4_mini_medium \
  --run-id p3_codex_split_gpt54mini_medium_001
```

The script reads agents directly from `subagent/<visual-variant>/`, infers the
harness from the variant name unless `--harness` is supplied, and installs only
the requested visible visual-agent topology:

- Codex variants install to `.codex/agents/`.
- Claude variants install to `.claude/agents/`.
- `--visual-setting general` installs the single general visual agent.
- `--visual-setting split` installs the scoped split agents.

It also copies DexHoldem v2 `visual_guidelines/` into the problem folder, then
writes:

```text
bench/problems/pN/runs/<run-id>/agent_manifest.json
bench/problems/pN/runs/<run-id>/harness_prompt.md
bench/problems/pN/runs/<run-id>/visual_raw/
```

`agent_manifest.json` includes a `version` block with SHA-256 hashes and sizes
for the preflight script, selected visual source agents, and visual guidelines.

By default, each install first cleans the previous active install surface while
preserving states, caches, and previous run records. Use `--no-clean` only when
you intentionally want to keep existing active files.

List available variants:

```bash
python3 perception_eval/preflight.py --list
```

Preview an install:

```bash
python3 perception_eval/preflight.py \
  --problem-dir bench/problems/p3 \
  --visual-setting general \
  --visual-variant codex_native_gpt5_4_mini_medium \
  --run-id preview \
  --dry-run
```

Clean a problem folder without installing a new variant:

```bash
python3 perception_eval/preflight.py --cleanup --problem-dir bench/problems/p3
```

Cleanup removes only the active visible-agent/runtime surface:
`.codex/agents/`, `.claude/agents/`, copied helper scripts, `config.yaml`,
`pyproject.toml`, and `visual_guidelines/`. It preserves `runs/`, `sN/`,
`s_current`, `hole_card_cache.json`, and `action_sequence.json`. Add
`--remove-runs` only when you intentionally want to delete run records too.

## Codex One-Run Wrapper

For Codex harness runs, use:

```bash
python3 perception_eval/run_codex_benchmark.py \
  --problem-dir bench/problems/p3 \
  --visual-setting split \
  --visual-variant codex_native_gpt5_4_mini_medium \
  --run-id p3_codex_split_gpt54mini_medium_003 \
  --model gpt-5.5 \
  --reasoning-effort medium \
  --service-tier fast
```

This performs:

```text
copy problem without runs/ -> preflight.py -> run-local CODEX_HOME/config.toml -> codex exec -C <isolated-problem> -> cleanup -> sync current run back
```

By default the wrapper creates an isolated problem copy outside the repo at
`../.dexholdem_perception_eval_work/`. The copy excludes prior `runs/`, active
agent/runtime installs, `.codex/`, `.claude/`, and Python caches. Preflight and
`codex exec` run inside that isolated copy, so the agent cannot inspect previous
run artifacts from the real problem folder or the parent Git checkout by
default. After Codex exits, only `runs/<run-id>/` from the isolated copy is
synced back to the source problem.

Inside the isolated copy, the wrapper creates a per-run Codex home at
`runs/<run-id>/.codex_home/`, copies only `auth.json` from the host Codex home,
and writes a run-specific `config.toml`. The config records:

```text
model / model_reasoning_effort / service_tier
sandbox_mode = "workspace-write"
agents.max_threads = 9
shell_environment_policy.inherit = "none"
```

The isolated workspace is the benchmark boundary: the run-local config does not
install a custom filesystem permission profile because Codex 0.125 currently
has shell-launch issues with restrictive profiles on macOS. Since prior
`runs/*` folders are not copied, they are not visible to the agent. Use
`--agent-max-threads N` to override the default split-agent parallel cap for one
run.

Useful isolation flags:

```text
--isolation-root PATH        parent directory for isolated problem copies
--keep-isolated-workspace    keep the temporary copy for debugging
--no-isolated-workspace      run directly inside --problem-dir
```

For a hard host-level guarantee that nothing outside the problem can even be
read, run each benchmark inside an OS sandbox or an isolated copied problem
tree that contains only the files the run may see. `codex exec` itself still
needs access to its auth/runtime environment to contact the model.

It writes wrapper artifacts into `runs/<run-id>/`:

```text
isolation_manifest.json
preflight_result.json
harness_version.json
codex_command.json
codex_stdout.txt
codex_stderr.txt
codex_exit.json
output_check.json
cleanup_result.json
```

`output_check.json` marks the run invalid unless Codex produced
`visual_summary.json`, `eval_report.md`, and at least one raw evidence file in
`visual_raw/`. The prompt requires the main harness to use visual subagents for
image perception and forbids the main harness from judging image content
directly.

If the harness creates a single sibling run directory with complete perception
outputs because it mistyped the long run id, the wrapper copies
`visual_raw/`, `visual_summary.json`, and `eval_report.md` back into the exact
expected run directory and records this in `output_recovery.json`.

`harness_version.json` records the Codex CLI version, Python version, wrapper
script hash, preflight script hash, model, reasoning effort, service tier,
sandbox mode, agent thread limit, and run-local config hash for fairness across
runs.

Use `--dry-run` to print the planned commands. Use `--keep-installed` when you
want to inspect the active `.codex/agents/` or `.claude/agents/` surface after Codex
finishes.

## Parallel Batch Launchers

Use the shared buffer engine when evaluating a full variant over many problems:

```bash
python3 perception_eval/run_parallel_buffer.py \
  --visual-variant codex_native_gpt5_4_mini_medium \
  --visual-setting split \
  --concurrency 6 \
  --model gpt-5.4-mini \
  --reasoning-effort low
```

Defaults:

```text
problems: p1 through p36
concurrency: 6 active subprocesses
visual setting: split
harness model: gpt-5.4-mini
harness reasoning effort: low
service tier: fast
```

The engine keeps a fixed-size run buffer: whenever one child finishes, the next queued
problem starts. Batch logs are written under `perception_eval/batch_runs/<batch-id>/`
as `manifest.json`, `events.jsonl`, `summary.json`, and per-child stdout/stderr
captures. Each child still writes its normal run artifacts into
`bench/problems/pN/runs/<run-id>/`.

Per-Codex-variant wrappers live in `perception_eval/launchers/`. Example:

```bash
perception_eval/launchers/run_codex_native_gpt5_4_mini_medium.sh
```

Override defaults with env vars or appended args:

```bash
VISUAL_SETTING=general CONCURRENCY=8 REASONING_EFFORT=low \
  perception_eval/launchers/run_codex_native_gpt5_4_mini_medium.sh \
  --run-prefix smoke_general --problem-list p1,p2 --dry-run
```

The current launchers target Codex-compatible variants because this repo has a
Codex one-run wrapper. Claude variants still need a `run_claude_benchmark.py`
equivalent before they can use the same buffer engine safely.

OpenRouter-backed Codex variants require `OPENROUTER_API_KEY` in the launcher
environment. The batch engine fails fast when that key is missing, and the
run-local Codex config injects:

```toml
[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"
wire_api = "responses"
request_max_retries = 4
```

Runs whose `visual_summary.json` reports `"status": "blocked"` are marked
invalid by `output_check.json`, even if placeholder files exist under
`visual_raw/`.
