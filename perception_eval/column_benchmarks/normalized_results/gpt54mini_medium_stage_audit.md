# GPT-5.4 Mini Medium Stage Audit

Batch: `batch003_gpt54mini_split_low_codex_native_gpt5_4_mini_medium_split`

| Problem | Stage from action_sequence | Existing normalized | Raw support | Evidence |
|---|---|---|---|---|
| p1 | `idle` | `acting` | `explicit_conflict:acting` | visual_summary.json: "stable": true, |
| p2 | `idle` | `None` | `implicit_support` | visual_summary.json: "scene_stable": true, |
| p3 | `acting` | `None` | `implicit_support` | visual_summary.json: "pose": "extended from right, mid-reach", |
| p4 | `acting` | `None` | `implicit_support` | visual_summary.json: "robot_behavior": "hand extended in lower-right robot-side area; still in progress, not idle" |
| p5 | `acting` | `None` | `implicit_support` | visual_summary.json: "moving": false, |
| p6 | `acting` | `None` | `implicit_support` | visual_summary.json: "scene_stable": true, |
| p7 | `atom_idle` | `acting` | `explicit_match` | visual_summary.json: "scene_stable": false, |
| p8 | `acting` | `None` | `insufficient_raw_support` | visual_summary.json: "scene_stable": { |
| p9 | `acting` | `in_hand` | `implicit_support` | eval_report.md: - Scene is stable enough to continue, but the robot hand still appears mid-motion. |
| p10 | `to_recover` | `acting` | `insufficient_raw_support` | visual_summary.json: "result": "unstable", |
| p11 | `down` | `down` | `explicit_match` | visual_summary.json: "loop_stage": "down", |
| p12 | `down` | `acting` | `explicit_match` | eval_report.md: - Community cards: no face-up community cards are visible; all board positions are unreadable/face-down. |
| p13 | `down` | `acting` | `insufficient_raw_support` | eval_report.md: - Five community-card positions are visible, but all are face-down/unreadable. |
| p14 | `idle` | `None` | `implicit_support` | visual_summary.json: "scene_stable": true, |
| p15 | `acting` | `None` | `explicit_match` | visual_summary.json: "robot_behavior": "uncertain, likely still in progress", |
| p16 | `atom_idle` | `atom_idle` | `explicit_match` | visual_summary.json: "loop_stage": "atom_idle", |
| p17 | `acting` | `None` | `implicit_support` | visual_summary.json: "scene_stable": false, |
| p18 | `idle` | `acting` | `explicit_conflict:acting` | visual_summary.json: "scene_stable": true, |
| p19 | `down` | `None` | `insufficient_raw_support` | eval_report.md: The scene is not yet stable enough to treat the robot action as complete. The robot hand is still in the right-card put-down area, so the action appears in progr... |
| p20 | `down` | `None` | `implicit_support` | eval_report.md: The scene is not settled yet. The visual subagents agree that the dexterous hand is still lowering/placing the right hole card back down in the lower-right robot... |
| p21 | `down` | `acting` | `insufficient_raw_support` | eval_report.md: - No readable community cards are visible; the board shows five face-down cards. |
| p22 | `acting` | `acting` | `implicit_support` | visual_summary.json: "motion": "not confirmable from single frame; appears paused mid-reach", |
| p23 | `to_recover` | `acting` | `insufficient_raw_support` | visual_summary.json: "result": "stable", |
| p24 | `to_recover` | `acting` | `insufficient_raw_support` | visual_summary.json: "scene_stable": true, |
| p25 | `idle` | `acting` | `implicit_support` | visual_summary.json: "stable": false, |
| p26 | `to_recover` | `acting` | `implicit_support` | visual_summary.json: "recovery_evidence": "no clear recovery behavior visible" |
| p27 | `idle` | `unknown` | `implicit_support` | visual_summary.json: "scene_stable": true, |
| p28 | `acting` | `acting` | `explicit_conflict:show_hand` | visual_summary.json: "scene_stable": true, |
| p29 | `idle` | `None` | `implicit_support` | visual_summary.json: "scene_stable": false, |
| p30 | `idle` | `None` | `insufficient_raw_support` | visual_summary.json: "scene_stable": false, |
| p31 | `acting` | `unknown` | `implicit_support` | eval_report.md: - The robot hand is low over the table, open, and not visibly moving. |
| p32 | `to_recover` | `to_recover` | `explicit_match` | visual_summary.json: "loop_stage": "to_recover", |
| p33 | `down` | `None` | `implicit_support` | visual_raw/robot_behavior_agent.md: - No obvious signs of dropped objects, damage, or a failed grasp attempt in this frame. |
| p34 | `idle` | `acting` | `insufficient_raw_support` | visual_summary.json: "scene_stable": false, |
| p35 | `win` | `acting` | `insufficient_raw_support` | visual_summary.json: "scene_stable": true, |
| p36 | `idle` | `acting` | `implicit_support` | visual_summary.json: "scene_stable": true, |
| p37 | `acting` | `None` | `implicit_support` | eval_report.md: - Robot behavior: still in progress, but safe to continue |
| p38 | `atom_idle` | `acting` | `insufficient_raw_support` | visual_summary.json: "scene_stable": true, |
| p39 | `atom_idle` | `unknown` | `implicit_support` | visual_summary.json: "scene_stable": "unknown", |
| p40 | `down` | `None` | `explicit_conflict:show_hand` | visual_summary.json: "unsafe_contact_visible": false, |
| p41 | `atom_idle` | `None` | `explicit_conflict:show_hand` | visual_summary.json: "scene_stable": true, |
| p42 | `atom_idle` | `acting` | `explicit_conflict:acting` | visual_summary.json: "scene_stable": false, |
| p43 | `win` | `None` | `explicit_match` | visual_summary.json: "phase": "collect_winnings", |
| p44 | `acting` | `show_hand` | `explicit_conflict:show_hand` | visual_summary.json: "progress": "still in progress", |
| p45 | `atom_idle` | `None` | `implicit_support` | visual_summary.json: "scene_stable": false, |
| p46 | `atom_idle` | `acting` | `implicit_support` | visual_summary.json: "scene_stable": true, |
| p47 | `acting` | `None` | `explicit_match` | visual_summary.json: "router_implication": "wait_for_motion_completion" |
| p48 | `atom_idle` | `None` | `implicit_support` | visual_summary.json: "scene_stable": true, |
| p49 | `atom_idle` | `None` | `implicit_support` | visual_summary.json: "scene_stable": false, |
| p50 | `acting` | `acting` | `explicit_match` | visual_summary.json: "intent": "wait_for_motion_completion", |
| p51 | `acting` | `None` | `explicit_match` | visual_summary.json: "robot": "The dexterous hand is over the middle-right of the table, with its fingers down on a chip stack as if placing or adjusting it. It does not look li... |
| p52 | `idle` | `acting` | `insufficient_raw_support` | visual_summary.json: "scene_stable": false, |
| p53 | `idle` | `None` | `insufficient_raw_support` | visual_summary.json: "scene_stable": false, |
| p54 | `idle` | `unknown` | `insufficient_raw_support` | visual_summary.json: "scene_stable": true, |
| p55 | `idle` | `acting` | `insufficient_raw_support` | visual_summary.json: "scene_stable": true, |
| p56 | `idle` | `None` | `implicit_support` | visual_summary.json: "scene_stable": true, |
| p57 | `lose` | `lose` | `explicit_match` | visual_summary.json: "loop_stage": "lose", |
| p58 | `win` | `show_hand` | `insufficient_raw_support` | visual_summary.json: "No poker-action reasoning was required because the state is a win/showdown perception step, not a choose_poker_action router branch." |
| p59 | `lose` | `None` | `explicit_match` | visual_summary.json: "likely_outcome": "robot_loses", |
| p60 | `lose` | `None` | `explicit_conflict:win` | visual_summary.json: "scene_stable": true, |
| p61 | `idle` | `None` | `implicit_support` | visual_summary.json: "scene_stable": false, |
| p62 | `idle` | `None` | `insufficient_raw_support` | visual_summary.json: "scene_stable": false, |
| p63 | `win` | `show_hand` | `explicit_conflict:show_hand` | eval_report.md: The safest merged parse is a stable showdown/show-hand frame with our turn indicator visible, but with unresolved blind assignment and approximate chip/bet count... |
| p64 | `acting` | `None` | `explicit_conflict:show_hand` | visual_summary.json: "scene_stable": true, |
