# Action

Based on: `01_parsed_state.md`

## Decision

Wait one more frame to verify the readable right hole card.

## Action JSON

```json
{
  "action": "wait",
  "reason": "verify_right_card_read",
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
  "preserved_loop_stage": null
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
