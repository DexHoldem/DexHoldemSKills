# Action

Based on: `01_parsed_state.md`

## Decision

Do not execute a robot movement while the scene is unstable. Treat waiting as
the committed action for this state, then create the next state after the delay.

## Action JSON

```json
{
  "action": "wait",
  "reason": "scene_unstable",
  "sleep_seconds": 30
}
```

## Execution

```json
{
  "stage": "completed",
  "started_at": "2026-05-01T00:00:00+00:00",
  "completed_at": "2026-05-01T00:00:30+00:00",
  "commands": [],
  "commands_completed": 0,
  "dry_run": true,
  "can_retry": true,
  "human_required": false,
  "preserved_loop_stage": "atom_idle"
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
