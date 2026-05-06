# Example State Timeline

Temporary example for the V2 folder cache design. This directory can be removed
after the refactor has real runtime output.

The example uses raw bench images copied from `bench/bench_raw/`:

- `exp_demo/s0/00_capture.jpg` from `bench/bench_raw/0.jpg`
- `exp_demo/s1/00_capture.jpg` from `bench/bench_raw/119.jpg`
- `exp_demo/s2/00_capture.jpg` from `bench/bench_raw/120.jpg`

The state folders demonstrate the intended lifecycle:

1. `00_capture.jpg` records the observation.
2. `01_parsed_state.md` records what the agent extracted.
3. `02_action.md` records the action taken from that parsed state.
4. Only after `02_action.md` exists should the next state folder be created.

`exp_demo/s_current` points to the latest example state, `s2`.

The example root also includes `hole_card_cache.json` and
`action_sequence.json`, matching the V2 runtime layout. The action sequence
keeps the cached translator `plan` plus mutable step statuses. In this demo,
missing cached hole cards cause a `view_card` action sequence, not a
human-help request. `hole_card_cache.json` also includes the one-time
blind/dealer assignment recognized from the first state image.
