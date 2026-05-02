# DexHoldem Perception Step

## Outcome

- Turn detection: `our turn`
- Scene stability: `unstable`
- Showdown state: `show_hand`

## Evidence

- The white turn button is visible near the lower-left robot seat and reads `Your Turn`.
- The robot arm is extended over the table and is still occluding part of the play area, so the frame is not stable enough for an action decision.
- Two community cards are visible: `Ts` and `Jh` with slight uncertainty on the suit of the second card.
- The robot-held hole card is not readable in this frame.
- Current bet read:
  - Opponent/top side: `2 blue (10)` and `2 brown (100)`, slightly uncertain because of occlusion.
  - Robot/bottom side: `4 red (5)` and `2 blue (10)`.
- Blind assignment read:
  - Robot seat appears to be big blind.
  - Opponent seat appears to be dealer and small blind.
- Showdown reading:
  - Opponent cards appear face-up, but one card is only partially readable.
  - Robot cards also appear face-up, but one card is not fully readable.
  - The board is too occluded to compare hands reliably, so no win/lose call was made.

## Action Taken

- No robot actions executed.
- No reasoning-agent poker action was requested or committed because the scene was still unstable and showdown visibility was incomplete.

## Files Written

- `runs/p44_codex_native_gpt5_4_medium_split_batch006_gpt54medium_split_low/visual_raw/`
- `runs/p44_codex_native_gpt5_4_medium_split_batch006_gpt54medium_split_low/visual_summary.json`
- `runs/p44_codex_native_gpt5_4_medium_split_batch006_gpt54medium_split_low/eval_report.md`
