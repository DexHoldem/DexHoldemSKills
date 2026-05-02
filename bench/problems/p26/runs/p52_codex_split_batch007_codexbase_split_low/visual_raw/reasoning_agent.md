Current situation: only blinds are known. Dealer is opponent, opponent posted the small blind `5`, and robot posted the big blind `10`. No parsed board state, hole cards, or action history are available, so the only safe inference is that there may be no additional bet to face.

Key rationale: with no confirmed raise and no current committed amount beyond the blinds, `check` is the most conservative action if the action is on the robot and no bet is outstanding. If the parsed state later shows a raise or a required call, this recommendation would need to be revalidated.

Recommended supported action JSON:
```json
{"action":"check"}
```

Validation caveat: confirm that the robot is actually to act and that no opponent raise occurred after the blinds; if either is false, `check` may be illegal and a different supported action will be needed.

