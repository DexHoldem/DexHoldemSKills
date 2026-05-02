Parsed state summary:
- table.scene_stable: true
- table.is_my_turn: true
- table.community_cards: []
- table.my_chips: {5: 4, 10: 3, 50: 2, 100: 2}
- table.opponent_chips: {5: 4, 10: 4, 50: 3, 100: 3}
- table.my_current_bet: 0
- table.opponent_bet: 0
- blinds: dealer=opponent, small_blind=opponent, big_blind=robot

Recommendation:
{"action":"check"}

Rationale:
Legal because it is my turn, there are zero community cards, and both current bets are 0, so there is no bet to call or raise. Checking preserves chips preflop.
