"""Shared benchmark prompt for Codex and Claude perception harnesses."""

DEFAULT_PROMPT = """Run the current DexHoldem perception step.

# Task
Read the capture image at `s_current/00_capture.jpg` and extract visual state.
Follow the field-specific guidelines in `visual_guidelines/`. Do not execute
robot actions, run helper scripts, or choose a poker action.

# Context files
- `action_sequence.json`: PRIOR workflow state (what was dispatched when the
  image was captured). Use as CONTEXT only — visual evidence determines the
  CURRENT state.
- `hole_card_cache.json`: cached robot hole cards for showdown comparison.
- `sN-1/01_parsed_state.md`: previous parsed state for inheriting durable fields.
- Do not inspect benchmark ground-truth files.

# Output
Write to `runs/<run_id>/`:
- `visual_raw/native.md` — raw perception evidence
- `visual_summary.json` — structured output (schema below)
- `eval_report.md` — brief summary of evidence and merging

Schema for `visual_summary.json`:
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

Field values:
- `loop_stage`: idle, acting, atom_idle, down, to_recover, win, lose, show_hand
- `blind`: big_blind, small_blind, none
- `showdown_outcome`: win, lose, tie, not_showdown
- Chip fields: objects with keys "5", "10", "50", "100" (integer counts)
- `uncertain_fields`: field names with inherited/inferred/low-confidence values

Do not write null or placeholder values — every field needs a concrete estimate.
Verify outputs exist before finishing.
"""
