"""Shared benchmark prompt for Codex and Claude perception harnesses."""

DEFAULT_PROMPT = """Run the current DexHoldem perception step.

Use the local setup and visible visual subagents.
The main agent's only job is to launch the needed visual subagents, merge their
returned evidence, write the requested files, verify those files exist, and
stop.
Do not execute robot actions.
Do not perform image perception in the main agent; merge subagent evidence only.
Do not run router.py, state.py, executor.py, or any helper script.
Do not call the reasoning agent or choose a poker action.
Run independent visual subagents in parallel whenever possible. If the runtime
agent limit prevents full parallelism, run them in waves; do not serialize them
unless a dependency or limit requires it.

Output policy:
- Do not write null, "unknown", or placeholder values in visual_summary.json.
- Every required field must contain a concrete best estimate.
- When direct visual evidence is incomplete, first inherit durable state from
  `sN-1/01_parsed_state.md`, `action_sequence.json`, or `hole_card_cache.json`
  when that state should persist physically. Otherwise choose the most likely
  value from current visual evidence and poker/workflow context.
- Add a field name to `uncertain_fields` whenever its value is inherited,
  inferred, or low confidence.

Current state and context:
- `s_current` points to the latest state directory.
- The latest capture is `s_current/00_capture.jpg`.
- `action_sequence.json` shows the PRIOR workflow state — what action was
  dispatched when the image was captured. Use it as context (e.g., "robot was
  pushing a chip"), but determine the CURRENT state from visual evidence
  (e.g., "chip push completed" or "chip push failed").
- `hole_card_cache.json` contains previously viewed robot hole cards. Use for
  showdown hand comparison when robot cards are face-down but were cached.
- Do not inspect benchmark ground-truth files.

Subagent inputs and conditions:
- `scene_stability_agent`: always pass `s_current/00_capture.jpg` and the
  previous state image, usually `sN-1/00_capture.jpg`. If there is a dispatched
  robot atom, also pass the last clearly settled pre-action image when
  available. The raw evidence must name the compared images. If the agent only
  inspects one image or cannot access the previous image, infer the most likely
  true/false value from current image and previous parsed state, and add
  `scene_stable` to `uncertain_fields`.
- `robot_behavior_agent`: pass `s_current/00_capture.jpg`, the previous state
  image, and action-sequence context including `loop_stage`, `current_step`,
  and step statuses. Ask for hand pose, held object, near-rest status,
  action progress, safety, retryability, and human-help concerns.
- `turn_detection_agent`: pass `s_current/00_capture.jpg`; ask only whether
  the physical turn marker indicates it is our turn.
- `blind_button_recognition_agent`: pass `s_current/00_capture.jpg`; use
  two-player blind/dealer rules only when the button evidence is visible.
- `community_cards_agent`: pass `s_current/00_capture.jpg`; report community
  cards left to right. For visible but unreadable or occluded community cards,
  inherit the previous known board when physically durable; otherwise choose the
  most likely card string and add `community_cards` to `uncertain_fields`.
- `held_card_recognition_agent`: call only when the robot hand appears to
  hold or expose a card, or when cached workflow context says a card-view atom
  is active. Pass `s_current/00_capture.jpg`; do not infer hidden cards.
- `chip_recognition_agent`: call for chip-inventory columns. Pass
  `s_current/00_capture.jpg` and ask for robot and opponent inventories,
  excluding current bet areas and button markers.
- `bet_recognition_agent`: call for current-bet columns. Pass
  `s_current/00_capture.jpg` and ask for robot and opponent current bet areas,
  excluding inventory stacks and button markers.
- `showdown_outcome_agent`: ALWAYS call when visual evidence shows showdown
  conditions: (1) 5 community cards are visible AND either player's hole cards
  are face-up, OR (2) opponent's hole cards appear folded/mucked toward the
  center. Do NOT skip this agent based on `action_sequence.json` — showdown
  is detected visually, not from workflow state. Pass `s_current/00_capture.jpg`,
  visible board and hole-card evidence, and cached robot hole cards if present.

Loop-stage merge rule:
- `action_sequence.json` shows the PRIOR workflow state (what was happening
  when the image was captured). Use it as CONTEXT, not as the answer.
- VISUAL EVIDENCE determines the CURRENT `loop_stage`. The perception task is
  to observe what the scene shows NOW, which may differ from the prior state.
- Use `acting` when visual evidence shows the hand still moving, reaching, or
  holding an object mid-action. If `action_sequence.json` says `acting` but
  the hand appears settled, the action may have completed — check visually.
- Use `atom_idle` when the scene is settled after an action atom but
  `action_sequence.json` still has pending steps (action completed, more to do).
- Use `idle` when the hand is near rest, no held card/chips, no large movement,
  and the action sequence is complete or empty.
- Use `to_recover` when visual evidence shows a harmless failed atom (e.g.,
  chip not fully pushed, card slightly misplaced) and the table is safe to retry.
- Use `down` when visual evidence shows unsafe conditions: dropped objects,
  scattered chips, blocked hand, or human intervention needed.
- Use `show_hand`, `win`, or `lose` when VISUAL showdown evidence is present:
  both players' hole cards face-up, or opponent folded. Determine outcome by
  comparing visible hands. Do NOT require `action_sequence.json` to say
  showdown — the game may have reached showdown since the last workflow update.
- If visual evidence is ambiguous, use `action_sequence.json` as context to
  inform the most likely state, and add `loop_stage` to `uncertain_fields`.

Use exactly this output directory: runs/<run_id>
Do not append the isolated workspace suffix or any other suffix to the run id.

Write:
- runs/<run_id>/visual_raw/
- runs/<run_id>/visual_summary.json
- runs/<run_id>/eval_report.md

`visual_summary.json` must use this nested schema matching state cache format:

```json
{
  "loop_stage": "idle",
  "blind": "big_blind",
  "showdown_outcome": "not_showdown",
  "table": {
    "scene_stable": true,
    "is_my_turn": true,
    "community_cards": [],
    "my_chips": {"5": 4, "10": 3, "50": 3, "100": 3},
    "opponent_chips": {"5": 4, "10": 4, "50": 3, "100": 3},
    "my_current_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "opponent_bet": {"5": 0, "10": 0, "50": 0, "100": 0},
    "uncertain_fields": []
  }
}
```

Field rules:
- `loop_stage`: one of idle, acting, atom_idle, down, to_recover, win, lose,
  show_hand
- `blind`: big_blind, small_blind, or none
- `showdown_outcome`: win, lose, tie, or not_showdown
- `table.scene_stable`: true or false
- `table.is_my_turn`: true or false
- `table.community_cards`: list of card strings like Ah, Td, 6s; omit only
  absent cards or face-down cards that are not part of the community board
- `table.my_chips`, `table.opponent_chips`, `table.my_current_bet`,
  `table.opponent_bet`: each an object with exactly the denomination keys
  `5`, `10`, `50`, `100`; values are integer count best estimates
- `table.uncertain_fields`: list of field names whose values are uncertain

`runs/<run_id>/visual_raw/` must contain at least one real evidence file.
Do not claim raw evidence exists unless the file exists on disk. Before your
final response, verify the three requested outputs and the non-empty
`visual_raw/` directory.
Keep the final response brief; do not repeat the full report content.
"""
