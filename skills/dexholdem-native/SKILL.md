---
name: texas-holdem-robot
description: "Texas Hold'em poker robot for physical play. Captures frames from a local webcam, extracts game state via vision, makes strategic decisions, and executes actions through a robot policy process. Includes termination detection via frame-diff + vision confirmation. Use when operating a physical poker-playing robot."
metadata:
  author: anyagent
  version: "1.0.0"
---

# Texas Hold'em Robot

Play poker with a physical robot. This skill runs a continuous loop:

1. **Capture** a frame from the local webcam
2. **Vision model** extracts game state from the image
3. **Decision model** produces an action
4. **Robot policy** executes the action via a remote PyAutoGUI service (HTTP request → click/paste on the remote machine's terminal)
5. **Termination detection** confirms action completion, then sends Ctrl+C via the remote service
6. **Log** the game state and repeat

Configuration is in `config.yaml`, with prompts in `vision_prompt.md`, `prompt.md`, and `termination_prompt.md`.

## Setup check (run this FIRST, before anything else)

Before starting, verify the skill is configured:

1. Read `config.yaml` from this skill's directory.
2. Check if the environment variable named in `api_key_env` is set (e.g., run `echo $OPENROUTER_API_KEY`). If per-model overrides exist (`vision.api_key_env` or `decision.api_key_env`), check those too.
3. **If the variable is empty or unset**, stop and tell the user:

   > **texas-holdem-robot skill needs setup.** Set your API key:
   >
   > 1. Get an API key from your provider (default: [OpenRouter](https://openrouter.ai/keys))
   > 2. Export it: `export OPENROUTER_API_KEY="sk-..."`
   > 3. Optionally edit `<path-to-skill>/config.yaml` to change providers, models, or hyperparameters

   Replace `<path-to-skill>` with the actual path to this skill's directory. Then stop — do not proceed.

4. Verify the capture script works: run `python3 capture.py --help` from this skill's directory.
5. Verify the robot policy script exists: check that the command in `robot.command_template` (default: `python policy.py`) references an accessible script on the remote server. If unsure, the user should confirm the remote path.
6. Verify the action translator works: run `python3 action_translator.py --help` from this skill's directory.
7. Verify the remote PyAutoGUI service is reachable: `python3 remote_exec.py --action calibrate` — this sends a request to the service at `remote_terminal.host` and returns the current mouse position on the remote machine. If it fails, check that the service is running and the host/port in config.yaml are correct.
8. Ask the user to position the terminal window (with SSH session) on the remote machine's screen. Update `remote_terminal.click_x/click_y` in config.yaml with coordinates that land inside that terminal window.
9. Test the remote terminal connection: `python3 remote_exec.py --action execute --command 'echo test'` — ask the user to visually confirm "test" appears in the remote terminal.
10. **If everything checks out**, proceed to the game loop.

## Game loop workflow

This skill is **loop-only** — there is no single-shot mode. The robot needs continuous operation.

1. Read `config.yaml` — load `capture`, `loop`, `vision`, `decision`, `robot`, `termination`, and `logging` configs.
2. Read `vision_prompt.md`, `prompt.md`, and `termination_prompt.md` from this skill's directory.
3. Resolve API key(s) from the environment variable(s) specified in `config.yaml`.
4. Initialize round counter to 0.
5. **Loop start:**

   - **a. Capture**: Run the capture command from `config.yaml` (`capture.command`). The command prints the captured image path to stdout. Log: `[Loop] Capture #N — webcam frame`

   - **b. Vision call**: Base64-encode the captured image and send to the vision model with `vision_prompt.md` as the system prompt to extract game state (includes `is_my_turn`, `game_phase`, `action_prompt`, chip denominations, and `hand` which may be `[]`).

   - **c. Check game_phase**: If `game_phase` is `"game_over"` — stop the loop and report the final state to the user. If `"between_hands"` or `"showdown"` — log the state, wait `loop.poll_interval` seconds, continue to next iteration.

   - **d. Card viewing check**: If `hand` is `[]` (empty — cards not yet viewed):
     1. Run the action translator: `python3 action_translator.py --action '{"action": "view_card"}'`
     2. Parse the output as a JSON array of commands (will be 3 commands: `pick_up_card`, `view_card`, `put_down_card`).
     3. Execute the commands sequentially using the per-command execution flow (step h below).
     4. **Dedicated card read**: After all view_card commands complete, capture a new frame and run another vision call to extract the hand.
     5. If `hand` is still `[]`, log a warning and wait `loop.poll_interval` seconds, continue to next iteration.
     6. Log: `[Cards] Hand detected: Ks Qd`

   - **e. Not my turn**: If `is_my_turn` is `false` — wait `loop.poll_interval` seconds, continue to next iteration.

   - **f. My turn — Decision call**: If `is_my_turn` is `true` — send the game state JSON to the decision model with `prompt.md` as the system prompt. The response includes `action`, `bet_chips`, and other fields.

   - **g. Action translation**: Run the action translator to decompose the poker action into robot commands:
     1. Run: `python3 action_translator.py --action '<decision JSON>' --chips '<my_chips JSON from vision>'` (pass the full decision JSON as the `--action` argument, and the `my_chips` array from the vision output as `--chips`). The `--chips` argument is optional — if the vision model didn't detect chip denominations, omit it and the translator falls back to amount-only mode.
     2. Parse stdout as a JSON array of command objects.
     3. Log: `[Translator] Action "raise" → 2 commands: pick_chips, place_bet`
     4. If the array is empty (e.g., `call` with `bet_chips: 0`), skip execution.

   - **h. Sequential command execution (remote terminal)**: For each command in the translated sequence:
     1. **Check the `local` flag**: If the command has `"local": true`, execute its `command` string directly as a local shell command (fire-and-forget background process). Log: `[Local] <command> — PID: <pid>`. Skip termination detection and proceed to the next command.
     2. **Build the command string**: Substitute the command JSON into `robot.command_template` (replace `{command}` with the JSON-encoded command object). Call this `policy_cmd`.
     3. **Set `attempt = 0`**.
     4. **Execute via remote terminal**:
        ```bash
        python3 remote_exec.py --action execute --command '<policy_cmd>'
        ```
        Log: `[Remote] Command 1/2: pick_chips (amount: 100) — typed to terminal (attempt N)`
     5. **Run per-command termination detection** (same inner loop as before: webcam frame capture → frame_diff → stability check → vision model with termination_prompt.md). Changes:
        - No PID tracking or process crash detection
        - When `action_completed: true` → send Ctrl+C, log success, exit inner loop
        - When timeout or `not_done_count >= termination.max_not_done_retries` → send Ctrl+C, increment `attempt`
     6. **After inner loop exits**:
        - Send Ctrl+C: `python3 remote_exec.py --action send_ctrlc`
        - Wait `remote_terminal.ctrlc_delay` seconds
        - If action was completed → Log: `[Remote] Command 1/2: completed (Ctrl+C sent)` → proceed to next command
        - If action was NOT completed and `attempt < remote_terminal.max_retries` → Log: `[Remote] Command 1/2: retry #N` → wait `remote_terminal.retry_delay`, go back to step 4
        - If `attempt >= max_retries` → Log: `[Remote] Command 1/2: FAILED after N retries` → abort remaining commands

   - **i. Log game state**: Append a JSONL entry to `logging.game_state_log` with: `timestamp` (ISO 8601), `round` (counter), `game_state` (vision output), `decision` (decision output), `termination` (per-command termination results). Log: `[Log] State appended to <log_path>`

   - **j. Increment round counter**. If `loop.max_rounds` > 0 and counter >= `loop.max_rounds`, stop the loop.

   - **k.** Wait `loop.poll_interval` seconds, continue to next iteration.

6. **Loop end** — stop on game over, user interrupt (Ctrl+C), or when `loop.max_rounds` is reached (if non-zero).

## Termination detection (per-command)

After executing a command via the remote terminal, run this inner loop to detect when that specific command is complete:

1. Initialize a rolling frame buffer (max size: `termination.history_size`).
2. Set `not_done_count` to 0.
3. **Inner loop** (every `termination.check_interval` seconds):

   - **a.** Run the capture command to get a new webcam frame. Add it to the rolling buffer. Log: `[Termination] Frame #N diff: <value or N/A>`

   - **b.** If the buffer has fewer than 2 frames, continue (log diff as `N/A`).

   - **c.** Compute the pixel diff between the two most recent frames using `frame_diff.py`:
     ```bash
     python3 frame_diff.py <prev_frame> <latest_frame>
     ```
     The script prints a float 0.0-1.0 to stdout.

   - **d.** If diff >= `termination.stability_threshold` — scene is still changing, continue.

   - **e.** If diff < `termination.stability_threshold` — scene is stable. Log: `[Termination] Frame #N diff: <value> — STABLE`

   - **f.** Make a **termination vision call**: base64-encode the latest frame and send to the vision model with `termination_prompt.md` as the system prompt. Include the specific robot sub-command in the user message (e.g., "The attempted command was: `pick_chips` with args: `{\"amount\": 100}`").

   - **g.** Parse the response JSON. If `action_completed` is `true`:
     - Log: `[Termination] Vision confirmation: action completed`
     - Exit the inner loop (Ctrl+C is sent in step h.6 of the main loop).

   - **h.** If `action_completed` is `false`:
     - Increment `not_done_count`.
     - If `not_done_count` >= `termination.max_not_done_retries`:
       - Log: `[Termination] Max retries reached — action not completed`
       - Exit the inner loop (Ctrl+C and retry logic handled in step h.6 of the main loop).
     - Otherwise, continue the inner loop (wait for the next frame).

4. **Timeout**: Track total elapsed time since the inner loop started. If elapsed >= `termination.timeout`:
   - Log: `[Termination] Timeout after <N>s`
   - Exit the inner loop (Ctrl+C and retry logic handled in step h.6 of the main loop).

5. **Capture failure mid-termination**: If the capture command fails during the inner loop (e.g., webcam failure), log the error and continue to the next iteration of the inner loop (do not abort termination detection).

## Robot policy execution (remote terminal)

Commands are executed on a remote server via a PyAutoGUI HTTP service. The agent sends HTTP requests to the service (at `remote_terminal.host`), which performs click/paste/Ctrl+C operations on the remote machine's terminal window. The `robot.command_template` in `config.yaml` specifies the command template. The `{command}` placeholder is replaced with the JSON-encoded robot sub-command.

Example: if the translator outputs `{"command": "pick_chips", "args": {"amount": 100}}` and the config has `"python policy.py --action '{command}'"`, the command string is:

```
python policy.py --action '{"command": "pick_chips", "args": {"amount": 100}}'
```

Execute via remote terminal (sends HTTP POST to the remote service):

```bash
python3 remote_exec.py --action execute --command 'python policy.py --action '\''{"command": "pick_chips", "args": {"amount": 100}}'\'''
```

To send Ctrl+C (terminate the running command in the remote terminal):

```bash
python3 remote_exec.py --action send_ctrlc
```

To get the current mouse position on the remote machine (for calibration):

```bash
python3 remote_exec.py --action calibrate
```

The `remote_exec.py` CLI is a thin HTTP client — it requires no local pyautogui/pyperclip installation. Only `pyyaml` is needed (for reading config.yaml).

### Action translator

The `robot.translator_command` in `config.yaml` translates a poker decision into a sequence of robot commands. The `{action_json}` placeholder is replaced with the decision model's full JSON output.

```bash
python3 action_translator.py --action '{"action": "call", "bet_chips": 50}'
# Output: [{"command": "pick_chips", "args": {"amount": 50}}, {"command": "place_bet", "args": {}}]
```

## Game state logging

Each round appends a JSONL entry to `logging.game_state_log` (default: `/tmp/poker_session_log.jsonl`). Format:

```json
{
  "timestamp": "2026-03-08T14:30:00Z",
  "round": 3,
  "game_state": { "hand": ["Ks", "Qd"], "community_cards": ["7h", "9c", "3s"], "...": "..." },
  "decision": { "action": "raise", "amount": 150, "bet_chips": 100, "reasoning": "...", "confidence": 0.68 },
  "termination": {
    "commands": [
      {"command": "pick_chips", "frames_captured": 2, "final_diff": 0.02, "vision_confirmed": true, "attempts": 1},
      {"command": "place_bet", "frames_captured": 3, "final_diff": 0.01, "vision_confirmed": true, "attempts": 1}
    ],
    "kill_signal": "Ctrl+C"
  }
}
```

The log file persists across the session. Read it to review past hands or track performance.

## Image input

Supported formats: **PNG**, **JPG/JPEG**, **GIF**, **WebP**.

Base64-encode the image:
```bash
BASE64=$(base64 -i <image_path>)
```

Detect the MIME type from the file extension:
- `.png` -> `image/png`
- `.jpg` / `.jpeg` -> `image/jpeg`
- `.gif` -> `image/gif`
- `.webp` -> `image/webp`

**Important**: Base64-encoded images are too large for shell command-line arguments. Always write the JSON payload to a temp file and use `curl -d @<file>` instead of inline `-d '{...}'`. See curl templates below.

## Curl templates — Vision call (OpenAI-compatible)

For providers `openrouter` and `openai`. Write the payload to a temp file to avoid command-line length limits:

```bash
BASE64=$(base64 -i <image_path>)

cat > /tmp/vision_payload.json <<PAYLOAD_EOF
{
  "model": "<vision.model from config.yaml>",
  "temperature": <vision.temperature from config.yaml>,
  "max_tokens": <vision.max_tokens from config.yaml>,
  "top_p": <vision.top_p from config.yaml>,
  "messages": [
    {"role": "system", "content": "<contents of vision_prompt.md>"},
    {"role": "user", "content": [
      {"type": "image_url", "image_url": {"url": "data:image/<format>;base64,${BASE64}"}}
    ]}
  ]
}
PAYLOAD_EOF

curl -s $ENDPOINT \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d @/tmp/vision_payload.json
```

The response JSON has `.choices[0].message.content` — parse that as the game state JSON.

## Curl templates — Vision call (Anthropic)

For provider `anthropic`. Write the payload to a temp file to avoid command-line length limits:

```bash
BASE64=$(base64 -i <image_path>)

cat > /tmp/vision_payload.json <<PAYLOAD_EOF
{
  "model": "<vision.model from config.yaml>",
  "max_tokens": <vision.max_tokens from config.yaml>,
  "temperature": <vision.temperature from config.yaml>,
  "top_p": <vision.top_p from config.yaml>,
  "system": "<contents of vision_prompt.md>",
  "messages": [
    {"role": "user", "content": [
      {"type": "image", "source": {"type": "base64", "media_type": "image/<format>", "data": "${BASE64}"}}
    ]}
  ]
}
PAYLOAD_EOF

curl -s https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d @/tmp/vision_payload.json
```

The response JSON has `.content[0].text` — parse that as the game state JSON.

## Curl templates — Termination vision call

Use the same curl format as the vision call above, but with `termination_prompt.md` as the system prompt instead of `vision_prompt.md`. Add the attempted action as a text block in the user message:

**OpenAI-compatible:**
```bash
cat > /tmp/termination_payload.json <<PAYLOAD_EOF
{
  "model": "<vision.model from config.yaml>",
  "temperature": <vision.temperature from config.yaml>,
  "max_tokens": <vision.max_tokens from config.yaml>,
  "top_p": <vision.top_p from config.yaml>,
  "messages": [
    {"role": "system", "content": "<contents of termination_prompt.md>"},
    {"role": "user", "content": [
      {"type": "image_url", "image_url": {"url": "data:image/<format>;base64,${BASE64}"}},
      {"type": "text", "text": "The attempted command was: <command_name> with args: <args_json>"}
    ]}
  ]
}
PAYLOAD_EOF

curl -s $ENDPOINT \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d @/tmp/termination_payload.json
```

**Anthropic:**
```bash
cat > /tmp/termination_payload.json <<PAYLOAD_EOF
{
  "model": "<vision.model from config.yaml>",
  "max_tokens": <vision.max_tokens from config.yaml>,
  "temperature": <vision.temperature from config.yaml>,
  "top_p": <vision.top_p from config.yaml>,
  "system": "<contents of termination_prompt.md>",
  "messages": [
    {"role": "user", "content": [
      {"type": "image", "source": {"type": "base64", "media_type": "image/<format>", "data": "${BASE64}"}},
      {"type": "text", "text": "The attempted command was: <command_name> with args: <args_json>"}
    ]}
  ]
}
PAYLOAD_EOF

curl -s https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d @/tmp/termination_payload.json
```

## Curl templates — Decision call (OpenAI-compatible)

For providers `openrouter` and `openai`:

```bash
curl -s $ENDPOINT \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "<decision.model from config.yaml>",
    "temperature": <decision.temperature from config.yaml>,
    "max_tokens": <decision.max_tokens from config.yaml>,
    "top_p": <decision.top_p from config.yaml>,
    "messages": [
      {"role": "system", "content": "<contents of prompt.md>"},
      {"role": "user", "content": "<game state JSON>"}
    ]
  }'
```

The response JSON has `.choices[0].message.content` — parse that as the action JSON.

## Curl templates — Decision call (Anthropic)

For provider `anthropic`:

```bash
curl -s https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "<decision.model from config.yaml>",
    "max_tokens": <decision.max_tokens from config.yaml>,
    "temperature": <decision.temperature from config.yaml>,
    "top_p": <decision.top_p from config.yaml>,
    "system": "<contents of prompt.md>",
    "messages": [
      {"role": "user", "content": "<game state JSON>"}
    ]
  }'
```

The response JSON has `.content[0].text` — parse that as the action JSON.

## Expected output

```
[Loop] Capture #1 — webcam frame
[Vision] game_phase: active, hand: [] — cards not viewed
[Translator] Action "view_card" → 4 commands: play_audio (local), pick_up_card, view_card, put_down_card
[Local] python3 play_audio.py wyyp.mp3 — PID: 12339
[Remote] Command 1/3: pick_up_card — typed to terminal (attempt 1)
[Termination] Command 1/3 — Frame #1 diff: N/A
[Termination] Command 1/3 — Frame #2 diff: 0.01 — STABLE
[Termination] Vision confirmation: pick_up_card completed
[Remote] Command 1/3: completed (Ctrl+C sent)
[Remote] Command 2/3: view_card — typed to terminal (attempt 1)
[Termination] Command 2/3 — Frame #1 diff: N/A
[Termination] Command 2/3 — Frame #2 diff: 0.02 — STABLE
[Termination] Vision confirmation: view_card completed
[Remote] Command 2/3: completed (Ctrl+C sent)
[Remote] Command 3/3: put_down_card — typed to terminal (attempt 1)
[Termination] Command 3/3 — Frame #1 diff: N/A
[Termination] Command 3/3 — Frame #2 diff: 0.01 — STABLE
[Termination] Vision confirmation: put_down_card completed
[Remote] Command 3/3: completed (Ctrl+C sent)
[Cards] Dedicated card read — capturing...
[Cards] Hand detected: Ks Qd

[Loop] Capture #2 — webcam frame
[Vision] Hand: Ks Qd | Board: 7h 9c 3s | is_my_turn: true
[Decision] call (bet_chips: 50)
[Translator] Action "call" → 2 commands: pick_chips, place_bet
[Remote] Command 1/2: pick_chips (amount: 50) — typed to terminal (attempt 1)
[Termination] Command 1/2 — Frame #1 diff: N/A
[Termination] Command 1/2 — Frame #2 diff: 0.02 — STABLE
[Termination] Vision confirmation: pick_chips completed
[Remote] Command 1/2: completed (Ctrl+C sent)
[Remote] Command 2/2: place_bet — typed to terminal (attempt 1)
[Termination] Command 2/2 — Frame #1 diff: N/A
[Termination] Command 2/2 — Frame #2 diff: 0.01 — STABLE
[Termination] Vision confirmation: place_bet completed
[Remote] Command 2/2: completed (Ctrl+C sent)
[Log] State appended to /tmp/poker_session_log.jsonl

[Loop] Capture #3 — webcam frame
[Vision] game_phase: active, is_my_turn: false — waiting 2s...

[Loop] Capture #7 — webcam frame
[Vision] game_phase: game_over — session ended.
```

## Provider endpoints

| Provider | Base URL |
|----------|----------|
| `openrouter` | `https://openrouter.ai/api/v1/chat/completions` |
| `openai` | `https://api.openai.com/v1/chat/completions` |
| `anthropic` | `https://api.anthropic.com/v1/messages` |

## Configuration

`config.yaml` has the following sections:

- **vision**: provider, model (must support image input), temperature (default 0.1 for deterministic extraction), max_tokens, top_p
- **decision**: provider, model, temperature (default 0.3), max_tokens, top_p
- **capture**: `command` (shell command to capture a webcam frame), `output_path` (where captured images are saved)
- **robot**: `command_template` (command template with `{command}` placeholder — this string is typed into the remote terminal), `translator_command` (command to translate poker actions to robot command sequences, with `{action_json}` placeholder)
- **remote_terminal**: `host` (URL of the PyAutoGUI HTTP service on the remote machine), `click_x`/`click_y` (screen coordinates of the terminal window on the remote machine), `focus_delay` (seconds after click), `ctrlc_delay` (seconds after Ctrl+C), `max_retries` (retry limit per command), `retry_delay` (seconds between retries)
- **termination**: `check_interval` (seconds between frame captures), `history_size` (rolling buffer size), `stability_threshold` (pixel diff threshold for "stable"), `timeout` (seconds before force-kill), `max_not_done_retries` (vision "not done" retries before force-kill)
- **loop**: `poll_interval` (seconds between captures, default 2), `max_rounds` (0 = unlimited)
- **logging**: `game_state_log` (path to JSONL log file for persistent game state tracking)
- **api_key_env** (top level): shared API key environment variable. Override per-model with `vision.api_key_env` or `decision.api_key_env`.

`vision_prompt.md` — system prompt for the vision model (image → game state extraction).

`prompt.md` — system prompt for the decision model (game state → action).

`termination_prompt.md` — system prompt for the termination vision call (latest frame + action → completion confirmation).
