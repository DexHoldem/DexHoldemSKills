---
name: dexholdem-native
description: "Physical poker robot using native agent vision and reasoning. Captures webcam frames, reads images directly to extract game state, reasons about poker strategy, and executes actions via a remote robot policy. No external API calls needed."
metadata:
  author: Tianzhe Chu
  version: "2.0.0"
---

# DexHoldem Native

Play poker with a physical robot using your own vision and reasoning — no external model APIs. This skill runs a continuous loop:

1. **Capture** a webcam frame
2. **Diff check** — compare with the previous frame to detect scene stability
3. **Recognize** — read the image natively, extract game state as JSON (guided by `vision_prompt.md`)
4. **Decide** — reason about the game state using `prompt.md` as strategy guide, produce an action
5. **Execute** — translate the action to robot commands and run them on the remote machine

Configuration is in `config.yaml`, with prompts in `vision_prompt.md` and `prompt.md`.

## Setup checklist

0. Activate the project venv before running any commands: `source .venv/bin/activate`
1. `python3 capture.py --help` — verify capture script.
2. `python3 action_translator.py --help` — verify translator.
3. `python3 remote_exec.py --action calibrate` — verify remote service reachable (check `remote_terminal.host` in `config.yaml` on failure).
4. Have user position the remote terminal window; update `remote_terminal.click_x`/`click_y` in `config.yaml`.
5. `python3 remote_exec.py --action execute --command 'echo test'` — confirm "test" appears in remote terminal.

## Game loop

Read `config.yaml` to load settings. Read `vision_prompt.md` and `prompt.md`. Initialize round counter to 0.

### Experiment init (once per session)

Create a new experiment directory to store state and frames:

```bash
python3 execution_state.py init
# Output: {working_dir}/experiments/exp20260319_001
```

This creates `{working_dir}/experiments/exp{date}_{seq}/frames/`, symlinks `{working_dir}/experiments/current` to it. All state and frames are saved here. `{working_dir}` is the directory where the agent is started.

### Recovery check (before first iteration)

Run `python3 execution_state.py load` to check for interrupted execution:

- **Exit 1 (no state)** — proceed normally.
- **`phase: executing`**, `commands_completed < len(command_sequence)` — interrupted mid-action. Capture a frame, compare visually against `last_verified_frame`. If the next command's effect is already visible, update `--completed <N+1>` and resume the sequence. If ambiguous, send Ctrl+C, `execution_state.py clear`, and restart the loop (fresh vision will re-derive game state).
- **`phase: verifying`** — recapture and re-verify.
- **Other** — clear state, proceed normally.

### Loop iteration

**a. Capture** — run the capture command from `config.yaml` (`capture.command`). It prints the image path to stdout. Save the frame to the experiment directory:

```bash
python3 execution_state.py save-frame /tmp/poker_latest.jpg --round <N> --label capture
```

**b. Frame diff check** — if a previous frame exists, compare frames:

```bash
python3 frame_diff.py <prev_frame> <current_frame>
```

Prints a float 0.0–1.0. If diff >= `stability_threshold` AND the previous iteration was executing a robot action → **"policy still running"**, wait `poll_interval`, recapture. If below threshold or no previous frame, proceed.

**c. Recognition** — `Read` the captured image. Following `vision_prompt.md`, extract game-state JSON (`hand`, `held_card`, `robot_state`, `community_cards`, `pot`, `position`, `is_my_turn`, `game_phase`, `my_chips`, etc.).

Save the recognition to status history:

```bash
python3 execution_state.py status-save --round <N> --robot-state <robot_state> --held-card <held_card> --last-action <last_action> --diff <diff_value>
```

- `game_phase: "game_over"` → stop loop, report final state.
- `game_phase: "between_hands"` → clear hand cache (`python3 execution_state.py hand-clear`), wait `poll_interval`, continue.
- `game_phase: "showdown"` or `is_my_turn: false` → wait `poll_interval`, continue.

**View-card workflow** — load hand cache (`python3 execution_state.py hand-load`) and status history (`python3 execution_state.py status-load --last 3`). If both `left` and `right` are cached, set `hand` to `[left, right]` and proceed to step d. Otherwise, determine the current state:

- **State i — Robot idle, hand incomplete**: `robot_state: "idle"`, frame diff is low (robot is nearly static), and fewer than 2 cards cached. → Proceed to step d with a `view_card` decision. The position is `"left"` if `left` is `null`, otherwise `"right"`.

- **State ii — Robot moving, view_card already dispatched**: `robot_state: "moving"`, fewer than 2 cards cached, and the last executed action (from status history) was `view_card`. The robot policy is still running. → **Do not proceed to decision.** Exit this iteration. The outer loop will wait `poll_interval` seconds and recapture.

- **State iii — Robot holding a readable card**: `robot_state: "holding_card"`, `held_card` is not `null`, and the card is not yet in the hand cache. → Cache it: `python3 execution_state.py hand-set --position <next_empty> --card <held_card>`. Then execute `put_down_card` (step e): `python3 action_translator.py --action '{"action": "put_down_card"}'`, run the returned commands via `remote_exec.py`. After execution, recapture and re-recognize.

**d. Decision** — reason about game-state JSON using `prompt.md` as strategy guide. Produce action JSON, e.g. `{"action": "call", "bet_chips": 50}`.

**e. Action translation and execution** — translate the action into robot commands:

```bash
python3 action_translator.py --action '<decision JSON>' --chips '<my_chips JSON>'
```

The `--chips` argument is optional (omit if chip denominations were not detected). Parse stdout as a JSON array of command objects.

Save execution state before starting: `python3 execution_state.py save --phase executing --action '<decision JSON>' --commands '<cmd_names>' --completed 0 --round <N>`.

For each command in the sequence:

1. **Local commands**: if the command has `"local": true`, run its `command` string as a local background process. Skip to next command.
2. **Remote commands**: substitute the command JSON into `robot.command_template` (replace `{command}` placeholder) to build `policy_cmd`. Execute:
   ```bash
   python3 remote_exec.py --action execute --command '<policy_cmd>'
   ```
3. **Wait for completion**: capture frames every `termination.check_interval` seconds (default 30 s — the robot moves slowly). **The completion condition depends on the action type:**
   - **`view_card` commands**: Do **NOT** use frame diff to decide completion. Instead, `Read` each captured frame and check whether `robot_state` is `"holding_card"` with a readable `held_card`. Only when the card is visually confirmed and cached should you proceed. Do **NOT** send Ctrl+C until the card has been read and cached — the robot moves slowly enough that low frame diff does not mean the policy has finished.
   - **All other commands**: use `frame_diff.py`. When diff < `termination.stability_threshold`, proceed to verification.
4. **Verify outcome**: set `execution_state.py update --phase verifying`. Read the stable frame via `Read` tool. Check whether the command's expected physical result is visible (e.g., `pick_chips` → chips missing from stack; `place_bet` → chips in pot; `pick_up_card` → card lifted; `put_down_card` → card on table).
5. **On success**: send Ctrl+C, wait `ctrlc_delay`. Save the verified frame: `execution_state.py save-frame <path> --round <N> --label verified`. Update: `execution_state.py update --completed <N+1> --frame <saved_path>`. Proceed to next command.
6. **On failure**: send Ctrl+C. If attempts < `max_retries` → wait `retry_delay`, re-execute from step 2. Otherwise → abort, `execution_state.py clear`.

After all commands complete successfully, clear the state: `python3 execution_state.py clear`.

**f. Increment round counter.** If `loop.max_rounds` > 0 and counter >= max, stop. Otherwise wait `loop.poll_interval` seconds, continue.

### Loop end

Stop on game over, user interrupt, or max rounds reached.

## Action translator reference

```bash
# Translate a poker action to robot commands
python3 action_translator.py --action '{"action": "call", "bet_chips": 50}'
# Output: [{"command": "pick_chips", "args": {"amount": 50}}, {"command": "place_bet", "args": {}}]

# View cards
python3 action_translator.py --action '{"action": "view_card"}'
# Output: [{"command": "pick_up_card", ...}, {"command": "view_card", ...}, {"command": "put_down_card", ...}]
```

## Remote execution reference

```bash
# Execute a command in the remote terminal
python3 remote_exec.py --action execute --command '<command_string>'

# Send Ctrl+C to the remote terminal
python3 remote_exec.py --action send_ctrlc

# Calibrate — get current mouse position on remote machine
python3 remote_exec.py --action calibrate
```

## Execution state reference

```bash
python3 execution_state.py init                    # create experiment dir, print path
python3 execution_state.py save --phase executing --action '<JSON>' --commands '<JSON>' --completed 0 --round 5
python3 execution_state.py update --completed 1 --frame <path>
python3 execution_state.py update --phase verifying
python3 execution_state.py save-frame /tmp/poker_latest.jpg --round 5 --label capture
python3 execution_state.py load                    # prints JSON, exit 1 if no state
python3 execution_state.py clear                   # remove state file (keep exp dir)
python3 execution_state.py hand-load               # print hand cache JSON
python3 execution_state.py hand-set --position left --card 9h   # cache a viewed card
python3 execution_state.py hand-clear              # reset hand cache (between hands)
python3 execution_state.py status-save --round 1 --robot-state idle --diff 0.01  # log status
python3 execution_state.py status-load --last 3    # print recent status entries
python3 execution_state.py status-clear            # clear status history
```

Experiment directory layout (`{working_dir}/experiments/`):
```
{working_dir}/experiments/
  current -> exp20260319_001/      # symlink to active experiment
  exp20260319_001/
    state.json                     # execution state
    hand_cache.json                # viewed hole cards cache
    frames/
      r001_001_capture.jpg         # round 1, frame 1
      r001_002_stable.jpg
      r001_003_verified.jpg
      r002_001_capture.jpg
```

## Configuration

`config.yaml` sections:

- **capture**: `command` (shell command to capture a frame), `output_path` (where images are saved)
- **robot**: `command_template` (template with `{command}` placeholder — typed into remote terminal), `translator_command` (action translator command with `{action_json}` placeholder)
- **remote_terminal**: `host` (PyAutoGUI service URL), `click_x`/`click_y` (terminal window coordinates on remote screen), `focus_delay`, `ctrlc_delay`, `max_retries`, `retry_delay`
- **termination**: `stability_threshold` (pixel diff threshold — below this means scene is stable), `check_interval` (seconds between diff checks), `timeout` (seconds before giving up)
- **experiments**: `base_dir` (where experiment folders are created, default `./experiments` relative to the working directory)
- **loop**: `poll_interval` (seconds between captures, default 2), `max_rounds` (0 = unlimited)
