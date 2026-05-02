# Action

## Action JSON

```json
{
  "action": "collect_winnings",
  "reason": "The parsed showdown state marks the robot as the hand winner; collect recognized bet chips."
}
```

## Execution

```json
{
  "stage": "planned",
  "dry_run": true,
  "can_retry": false,
  "human_required": false,
  "note": "The parsed showdown state marks the robot as the hand winner; collect recognized bet chips."
}
```

## Translation

```json
{
  "prefix": "reset",
  "commands": [],
  "command_steps": [],
  "sequence_steps": [
    "collect_winnings"
  ],
  "note": "Use recognized my_current_bet and opponent_bet chip counts to build the physical pull-back sequence."
}
```

## Commands

```json
[]
```
