# DexHoldem V2 TODO

Review date: 2026-05-01

## High Priority

1. Fix continuation actions overwriting the parent action sequence.

   `executor.py` starts a new `action_sequence.json` for every non-wait action.
   When `router.py` continues a `view_card` or `show_card` sequence by issuing
   `put_down_card`, the original sequence cache is overwritten. The cache then
   stops representing the full embodied sequence.

   Relevant files:

   - `scripts/executor.py`
   - `scripts/router.py`
   - `scripts/state.py`

2. Do not mark atom steps completed at command dispatch time.

   The executor currently calls `complete-step` immediately after sending each
   robot command. Physical success is only known after the next capture and
   visual parsing. If a chip/card action fails, `current_step` may already point
   to the next step, making `to_recover` retry or diagnose the wrong atom.

   Relevant files:

   - `scripts/executor.py`
   - `scripts/state.py`
   - `visual_guidelines/ROBOT_BEHAVIOR.md`

3. Make chip translation exact-change behavior explicit.

   `split_chips()` can use one larger chip when exact change is unavailable.
   Example: calling 15 with only a 50 chip available emits `push_chip_50_1`
   while `computed.physical_bet_chips` still reports 15. This is fragile for a
   physical table unless overpay/change-making is intentionally supported.

   Relevant files:

   - `scripts/action_translator.py`
   - `SKILL.md`

4. Remove or demote `workflow.py`.

   `workflow.py` is now a stale second router. It lacks cache validation,
   stage-specific field validation, uncertain-field handling, collection-count
   gating, and richer recovery context. It is still copied by preflight and
   listed as a useful command, so an agent can accidentally bypass `router.py`.

   Relevant files:

   - `scripts/workflow.py`
   - `scripts/preflight.py`
   - `STATE_CACHE.md`

## Medium Priority

5. Make `request_human` pause semantics explicit.

   `request_human` marks the action sequence `down`, but once `02_action.md`
   exists the router returns `begin_next`. That can capture the next state before
   the human has fixed anything. Decide whether `request_human` should block
   state creation, require an explicit resume action, or intentionally create a
   new waiting state.

   Relevant files:

   - `scripts/executor.py`
   - `scripts/router.py`
   - `SKILL.md`

6. Add concrete retry/recovery helpers.

   `retry_count` exists, and `router.py` can return `recover_retryable`, but no
   helper increments retry count, resets the failed step, or dispatches exactly
   the cached atom command. The main agent currently has to invent the mechanical
   retry path.

   Relevant files:

   - `scripts/state.py`
   - `scripts/router.py`
   - `scripts/executor.py`

7. Decide whether `collect_winnings` needs location-aware commands.

   The current translator computes `my_current_bet + opponent_bet` by
   denomination and emits `pull_chip_<denom>_<n>` steps. If physical pull
   policies depend on chip side or table region, the action sequence needs to
   preserve chip source zones.

   Relevant files:

   - `scripts/action_translator.py`
   - `visual_guidelines/BET_RECOGNITION.md`
   - `visual_guidelines/TABLE_GEOMETRY.md`

8. Define the post-hand reset path.

   `state.py clear-hand` exists, but the workflow does not clearly specify what
   happens after a completed win collection or a lost hand. The skill needs a
   concrete next-hand transition: cache clearing, blind refresh if buttons move,
   expected state folder action, and whether to stop or continue.

   Relevant files:

   - `scripts/state.py`
   - `SKILL.md`
   - `STATE_CACHE.md`

## Low Priority

9. Refresh example state action files.

   The current runtime executor writes `Execution`, `Translation`, and
   `Commands` blocks. The example `02_action.md` files use older hand-written
   shapes. They remain conceptually useful but are not faithful runtime
   examples.

   Relevant files:

   - `example_states/exp_demo/s0/02_action.md`
   - `example_states/exp_demo/s1/02_action.md`
   - `example_states/exp_demo/s2/02_action.md`

10. Remove macOS metadata files.

    `.DS_Store` files are present under the skill tree and should not ship with
    the skill.

    Relevant files:

    - `.DS_Store`
    - `example_states/.DS_Store`
    - `example_states/exp_demo/.DS_Store`
