state: s17
capture: /Users/ma-lab-hku/project/.dexholdem_perception_eval_work/p17_p17_codex_native_gpt5_5_low_general_batch012_gpt55low_general_low_8ejbvx10/p17/s17/00_capture.jpg

evidence:
- Source parsed state says loop_stage is `acting` and the dexterous hand is moving through the right hole-card put-down sequence.
- Source parsed state says `scene_stable` is `false`.
- Source parsed state says `is_my_turn` is `true`.
- Source parsed state says `community_cards` is empty.
- Source parsed state says the readable held card is `5d` from the right slot.
- Source action says to wait for the right-card put-down action to move and settle.

merged_judgment:
- The current frame should be treated as unstable / in-progress.
- This is not a showdown frame from the available text evidence.
- No betting change is visible in the parsed state; both current-bet maps are zeroed.
- The safest perception outcome is to wait for a settled frame before any downstream action reasoning.
