# Action

Based on: `01_parsed_state.md`

## Decision

Put down the viewed right hole card.

## Action JSON

```json
{
  "action": "put_down_card",
  "position": "right",
  "face_up": false
}
```

## Execution

```json
{
  "stage": "dispatched",
  "started_at": "2026-05-01T00:00:00+00:00",
  "commands": [
    "python TexasPoker/robot_client.py --server_ip localhost --obs_horizon 1 --instruction 11"
  ],
  "commands_total_in_sequence": 1,
  "command_index": 0,
  "commands_completed": 0,
  "commands_dispatched": 1,
  "dry_run": true,
  "can_retry": true,
  "human_required": false,
  "preserved_parent_sequence": true,
  "completed_at": "2026-05-01T00:00:00+00:00",
  "note": "Robot atom command dispatched. Complete the step only after visual atom_idle verification."
}
```

## Translation

```json
{
  "prefix": "ctrlc",
  "commands": [
    "python TexasPoker/robot_client.py --server_ip localhost --obs_horizon 1 --instruction 11"
  ],
  "command_steps": [
    "put_down_card"
  ],
  "sequence_steps": [
    "put_down_card",
    "verify_idle"
  ]
}
```

## Commands

```json
[
  "python TexasPoker/robot_client.py --server_ip localhost --obs_horizon 1 --instruction 11"
]
```
