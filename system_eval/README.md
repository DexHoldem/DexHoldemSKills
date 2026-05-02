# System Eval

`system_eval/preflight.py` creates a self-contained DexHoldem experiment
workspace for real system-level runs.

Default setup:

```bash
python3 system_eval/preflight.py --exp-name exp001
```

This creates `experiments/exp001/`, updates `experiments/current`, and installs:

- `skills/dexholdem-v2` copied to `.agent/skills/dexholdem-v2`
- `.claude/skills/dexholdem-v2` symlinked to the shared skill copy
- `.codex/skills/dexholdem-v2` symlinked to the shared skill copy
- split Codex visual subagents from `subagent/codex_native_gpt5_4_mini_medium/split`
- split Claude visual subagents from `subagent/claude_sonnet_4_6_medium/split`
- runtime helper script symlinks, `config.yaml`, `pyproject.toml`, `visual_guidelines`, `s0`, `s_current`, and the two state caches

Use `--dry-run` to inspect the planned setup without writing. Use `--force`
only when intentionally replacing the named experiment directory.

To also populate `s0/00_capture.jpg` during setup:

```bash
python3 system_eval/preflight.py --exp-name exp001 --uv-sync --capture-initial
```

For a hardware-free capture smoke test, use an existing image:

```bash
python3 system_eval/preflight.py --exp-name exp001 --capture-initial --camera-source path/to/image.jpg
```
