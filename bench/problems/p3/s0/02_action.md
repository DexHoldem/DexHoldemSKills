# Action

Based on: `01_parsed_state.md`

## Decision

The robot is idle, the scene is stable, the "Your Turn" marker is visible, and
the hole cards are still face-down. The committed action for this finished
historical state is to view the left hole card.

## Action JSON

```json
{
  "action": "view_card",
  "position": "left"
}
```

## Execution

```json
{
  "stage": "dispatched",
  "started_at": "2026-05-01T00:00:00+00:00",
  "commands": [
    "python TexasPoker/robot_client.py --server_ip localhost --obs_horizon 1 --instruction 0"
  ],
  "commands_total_in_sequence": 1,
  "command_index": 0,
  "commands_completed": 0,
  "commands_dispatched": 1,
  "dry_run": true,
  "can_retry": true,
  "human_required": false,
  "preserved_parent_sequence": false,
  "completed_at": "2026-05-01T00:00:00+00:00",
  "note": "Robot atom command dispatched. Complete the step only after visual atom_idle verification."
}
```

## Translation

```json
{
  "prefix": "reset",
  "commands": [
    "python TexasPoker/robot_client.py --server_ip localhost --obs_horizon 1 --instruction 0"
  ],
  "command_steps": [
    "pick_card"
  ],
  "sequence_steps": [
    "pick_card",
    "read_card",
    "put_down_card",
    "verify_idle"
  ]
}
```

## Commands

```json
[
  "python TexasPoker/robot_client.py --server_ip localhost --obs_horizon 1 --instruction 0"
]
```
