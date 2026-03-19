# Repository Guidelines

## Project Structure & Module Organization

This repository currently contains one skill package at `skills/texas-holdem-robot/`. Core Python entry points live directly in that directory: `capture.py` handles webcam capture, `action_translator.py` converts poker decisions into robot commands, `remote_exec.py` talks to the remote terminal service, `frame_diff.py` checks scene stability, and `play_audio.py` plays prompt audio. Configuration is in `config.yaml`. Prompt templates live in `prompt.md`, `vision_prompt.md`, and `termination_prompt.md`. Static assets are under `skills/texas-holdem-robot/audio/`.

## Build, Test, and Development Commands

This repo does not define a formal build system. Use the scripts directly from the skill directory:

- `python3 skills/texas-holdem-robot/capture.py --help`: inspect webcam capture options.
- `python3 skills/texas-holdem-robot/action_translator.py --help`: inspect action translation inputs.
- `python3 skills/texas-holdem-robot/remote_exec.py --action calibrate`: verify remote terminal connectivity.
- `python3 skills/texas-holdem-robot/frame_diff.py a.jpg b.jpg`: compare two frames.
- `python3 skills/texas-holdem-robot/play_audio.py --list`: list bundled audio cues.

Install dependencies before running scripts: `pip install pyyaml pillow`. Some scripts also require system tools such as `imagesnap`, `ffmpeg`, `ffplay`, or `afplay`.

## Coding Style & Naming Conventions

Follow existing Python style: 4-space indentation, snake_case for functions and variables, and short module-level docstrings. Keep scripts focused and CLI-driven. Prefer explicit argument parsing with `argparse` and return machine-readable JSON from command-line tools when practical. Keep configuration keys lowercase with underscore-separated names.

## Testing Guidelines

There is no committed automated test suite yet. For contributions, add targeted checks where possible and validate scripts through their CLI interfaces. Name future tests after the module they cover, for example `tests/test_action_translator.py`. At minimum, verify `--help` output, success paths, and error handling for malformed JSON or missing files.

## Commit & Pull Request Guidelines

The repository has no commit history yet, so use clear, imperative commit messages such as `Add retry handling to remote executor`. Keep each commit focused. Pull requests should include a short summary, note config or dependency changes, and describe how the change was validated. Include screenshots only when UI or vision-output behavior materially changes.

## Security & Configuration Tips

Do not commit API keys, local host addresses that are environment-specific, or generated logs from `/tmp`. Treat `config.yaml` as a template and prefer environment variables such as `OPENROUTER_API_KEY` for secrets.
