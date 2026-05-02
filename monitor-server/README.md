# DexHoldem Monitor

Real-time monitoring dashboard for DexHoldem agent experiments.

## Features

- **Live state tracking**: Displays current loop stage and activity (capturing, perceiving, reasoning, acting, re-executing, requesting human)
- **Safety counters**: Tracks waits, recoveries, failures, and human help requests
- **Capture preview**: Shows the latest screenshot from the experiment
- **Table state**: Displays chip counts and betting information
- **Human help alerts**: Highlights when human intervention is requested
- **Real-time updates**: WebSocket-based updates when experiment files change

## Installation

```bash
cd monitor-server
npm install
npm run build
```

## Usage

```bash
# Start with default experiment directories (./experiments, ./bench/problems)
npm start

# Specify custom experiment directory
npm start -- --exp-dir /path/to/experiments

# Specify port
npm start -- --port 8080

# Multiple experiment directories
npm start -- --exp-dir ./experiments --exp-dir ./bench/problems
```

Open `http://localhost:3000` in your browser.

## Experiment Directory Structure

The monitor expects experiments with this structure:

```
exp001/
├── action_sequence.json      # Current action state and safety counters
├── hole_card_cache.json      # Cached hole cards (optional)
├── human_help_request.json   # Present when human help is requested
├── s0/
│   ├── 00_capture.jpg        # Screenshot
│   ├── 01_parsed_state.md    # Parsed visual state (contains JSON)
│   └── 02_action.md          # Committed action
├── s1/
│   └── ...
```

## Loop Stages

| Stage | Color | Description |
|-------|-------|-------------|
| idle | Green | Waiting for turn or action |
| atom_idle | Green | Robot settled after atomic action |
| acting | Blue | Executing robot commands |
| to_recover | Orange | Recovering from failed action |
| down | Red | Error state, needs intervention |
| show_hand | Purple | Showdown phase |
| win | Green | Hand won |
| lose | Red | Hand lost |

## Activities

| Activity | Color | Description |
|----------|-------|-------------|
| capturing | Blue | Taking screenshot |
| perceiving | Purple | Parsing visual state |
| reasoning | Orange | Deciding next action |
| acting | Green | Executing action |
| re-executing | Red | Retrying failed action |
| requesting_human | Red (pulsing) | Waiting for human help |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/experiments` | List all detected experiments |
| `GET /api/experiments/:id/state` | Get full state for an experiment |
| `GET /api/experiments/:id/capture/:stateNum` | Get capture image |
| `WS /ws/:expId` | WebSocket for real-time updates |

## Human Help Workflow

When the agent requests human help:

1. `human_help_request.json` is created in the experiment directory
2. Monitor shows "Requesting Human" activity (pulsing red)
3. Human Help panel displays reason and resume options
4. "Human Helps" counter increments

After resolving:

```bash
# Acknowledge human help and clear the request
python3 state.py ack-human-help --reset-safety --set-stage to_recover
```

## Development

```bash
# Watch mode for TypeScript
npm run dev

# Rebuild after changes
npm run build
```

## Tech Stack

- **Backend**: Node.js, Express, WebSocket (ws), chokidar
- **Frontend**: Vanilla TypeScript, CSS
- **Build**: TypeScript compiler, esbuild
