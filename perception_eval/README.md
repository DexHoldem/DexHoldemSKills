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
the requested visible-agent topology:

- Codex variants install to `.codex/agents/`.
- Claude variants install to `.claude/agents/`.
- `--visual-setting general` installs the single general visual agent.
- `--visual-setting split` installs the scoped split agents.

It also copies DexHoldem v2 runtime scripts, `config.yaml`, `pyproject.toml`,
and `visual_guidelines/` into the problem folder, then writes:

```text
bench/problems/pN/runs/<run-id>/agent_manifest.json
bench/problems/pN/runs/<run-id>/harness_prompt.md
bench/problems/pN/runs/<run-id>/visual_raw/
```

`agent_manifest.json` includes a `version` block with SHA-256 hashes and sizes
for the preflight script, selected source agents, DexHoldem runtime scripts,
visual guidelines, `config.yaml`, and `pyproject.toml`.

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
preflight.py -> codex exec -C <problem-dir> ... -> cleanup
```

By default the wrapper invokes Codex with:

```text
-s workspace-write
--ephemeral
-c default_permissions="workspace_only"
-c permissions.workspace_only.filesystem."<problem-dir>"="read"
-c permissions.workspace_only.filesystem."<problem-dir>/**"="read"
-c permissions.workspace_only.filesystem."<problem-dir>/runs/<run-id>"="write"
-c permissions.workspace_only.filesystem."<problem-dir>/runs/<run-id>/**"="write"
-c sandbox_permissions=[]
-c shell_environment_policy.inherit=none
```

This uses the `workspace_only` filesystem permission profile from
`~/.codex/config.toml`: the home tree is denied by default, and the wrapper
injects exact per-run allow rules for the active problem folder. The problem
folder is readable, while only `runs/<run-id>/` is writable. The wrapper still
passes `workspace-write`, no extra writable directories, no sandbox permission
expansions, no inherited shell environment, and ephemeral sessions.

For a hard host-level guarantee that nothing outside the problem can even be
read, run each benchmark inside an OS/container sandbox or an isolated copied
problem tree that contains only the files the run may see. `codex exec` itself
still needs access to its auth/runtime environment to contact the model.

It writes wrapper artifacts into `runs/<run-id>/`:

```text
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

`harness_version.json` records the Codex CLI version, Python version, wrapper
script hash, preflight script hash, model, reasoning effort, service tier,
sandbox mode, and permission profile for fairness across runs.

Use `--dry-run` to print the planned commands. Use `--keep-installed` when you
want to inspect the active `.codex/agents/` or `.claude/agents/` surface after Codex
finishes.

## Docker-Isolated Codex Runs

For a stronger filesystem boundary, use the Docker wrapper:

```bash
python3 perception_eval/run_codex_benchmark_docker.py \
  --problem-dir bench/problems/p3 \
  --visual-setting split \
  --visual-variant codex_native_gpt5_4_mini_medium \
  --run-id p3_codex_split_gpt54mini_medium_004 \
  --model gpt-5.5 \
  --reasoning-effort medium \
  --service-tier fast \
  --build-image
```

This still runs host-side preflight and cleanup, but boxes the actual
`codex exec` process in Docker. The container receives only:

```text
/workspace                 read-write bind mount of --problem-dir
/codex-auth/auth.json       read-only bind mount of Codex auth.json
```

Codex copies the auth file into container-local `/tmp/codex-home`, then runs
with:

```text
CODEX_HOME=/tmp/codex-home
codex exec --ephemeral --ignore-user-config --ignore-rules --skip-git-repo-check
```

All edits to `runs/<run-id>/`, `visual_summary.json`, and `eval_report.md` are
made under `/workspace`, so they are automatically synced to the local problem
folder through the bind mount.

The default image tag is `dexholdem-codex-cli:0.125.0`, built from
[Dockerfile.codex](Dockerfile.codex). Use `--dry-run` to inspect the exact
`docker run` command before launching.
