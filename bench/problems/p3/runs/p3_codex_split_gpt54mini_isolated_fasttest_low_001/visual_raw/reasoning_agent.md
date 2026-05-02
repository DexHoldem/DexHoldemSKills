Current situation: it’s our turn, community cards are unreadable, and both bet areas are partially occluded. Visible chips suggest our committed bet is about `60` and the opponent’s visible committed bet is about `45`, but the opponent’s far-right chips may hide more.

Key rationale: with no readable hole cards and no reliable board texture, I should avoid a speculative raise. The safest supported action is to take the lowest-commitment action if no extra call is actually outstanding.

Recommended action JSON:
```json
{"action":"check"}
```

Validation caveat: if the occluded opponent chips mean their true committed bet exceeds ours, then `check` would be invalid and the correct supported action would instead be `call`.

