# Action

## Action JSON

```json
{
  "action": "continue_cached_action_sequence",
  "reason": "The atom has settled but the cached action sequence still has pending steps."
}
```

## Execution

```json
{
  "stage": "pending",
  "dry_run": true,
  "can_retry": true,
  "human_required": false,
  "note": "The atom has settled but the cached action sequence still has pending steps."
}
```

## Translation

```json
{
  "prefix": "reset",
  "commands": [],
  "command_steps": [],
  "sequence_steps": []
}
```

## Commands

```json
[]
```
