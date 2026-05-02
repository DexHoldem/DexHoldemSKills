# Action

Based on: `01_parsed_state.md`

## Decision

Wait for the right-card put-down action to move and settle.

## Action JSON

```json
{
  "action": "wait",
  "reason": "robot_action_in_progress",
  "sleep_seconds": 30
}
```

## Execution

```json
{
  "stage": "completed",
  "started_at": "2026-05-01T00:00:00+00:00",
  "completed_at": "2026-05-01T00:00:00+00:00",
  "commands": [],
  "commands_completed": 0,
  "dry_run": true,
  "can_retry": true,
  "human_required": false,
  "preserved_loop_stage": "acting"
}
```

## Translation

```json
{
  "prefix": null,
  "commands": [],
  "command_steps": [],
  "sequence_steps": []
}
```

## Commands

```json
[]
```
