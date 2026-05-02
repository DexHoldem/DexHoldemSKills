{
  "table_state": {
    "street": "flop_or_later_with_3_visible_community_cards",
    "community_cards_visible": [
      {"rank": "3", "suit": "clubs", "confidence": "medium"},
      {"rank": "5", "suit": "diamonds", "confidence": "high"},
      {"rank": "10", "suit": "clubs", "confidence": "high"}
    ],
    "community_cards_unclear": [
      "Two face-down cards/covered card backs are visible to the left of the exposed board; unclear whether these are undealt turn/river placeholders or other cards."
    ],
    "pot_area": {
      "visible_chips": true,
      "chip_count_confidence": "low",
      "notes": "Several chip stacks are visible around the central/top betting zones; exact pot total cannot be determined from image."
    }
  },
  "player_areas": {
    "bottom_center_player": {
      "hole_cards": [
        {"visibility": "face_down", "confidence": "high"},
        {"visibility": "face_down", "confidence": "high"}
      ],
      "dealer_button": true,
      "blind_button": "small blind",
      "chips_visible": true,
      "chips_or_bet": [
        {"denomination": "10", "count": 2, "confidence": "high"},
        {"denomination": "5", "count": 3, "confidence": "medium"}
      ],
      "notes": "White DEALER button and blue SMALL BLIND button are immediately above this player's card area."
    },
    "bottom_right_player": {
      "hole_cards": "not_visible_or_occluded",
      "chips_visible": true,
      "chips_or_bet": [
        {"denomination": "50", "count": 2, "confidence": "medium"},
        {"denomination": "100", "count": 1, "confidence": "medium"},
        {"denomination": "10", "count": 1, "confidence": "low"}
      ],
      "notes": "Partly occluded by robot arm/camera assembly."
    },
    "bottom_left_player_seat_6_area": {
      "hole_cards": "not_visible",
      "chips_visible": true,
      "chips_or_bet": [
        {"denomination": "5", "count": 3, "confidence": "medium"}
      ]
    },
    "left_middle_player": {
      "hole_cards": "not_visible",
      "chips_visible": true,
      "chips_or_bet": [
        {"denomination": "5", "count": 2, "confidence": "medium"}
      ]
    },
    "top_left_player": {
      "hole_cards": [
        {"visibility": "face_down", "confidence": "medium"},
        {"visibility": "face_down", "confidence": "medium"}
      ],
      "chips_visible": true,
      "chips_or_bet": [
        {"denomination": "5", "count": 4, "confidence": "low"},
        {"denomination": "10", "count": 6, "confidence": "low"}
      ],
      "notes": "Human player is holding cards near face; card faces are not visible."
    },
    "top_right_player_seat_1_area": {
      "hole_cards": [
        {"visibility": "face_down", "confidence": "medium"},
        {"visibility": "face_down", "confidence": "medium"}
      ],
      "chips_visible": true,
      "chips_or_bet": [
        {"denomination": "5", "count": 4, "confidence": "low"},
        {"denomination": "10", "count": 3, "confidence": "low"}
      ],
      "notes": "Partially occluded by robot hand/arm."
    }
  },
  "turn_indicators": {
    "explicit_turn_marker_visible": false,
    "active_player": "unknown",
    "dealer_button_location": "bottom_center_player",
    "small_blind_location": "bottom_center_player",
    "big_blind_location": "not_visible"
  },
  "robot_and_occlusion": {
    "robot_visible": true,
    "robot_pose": "arm/hand extended over upper-right table area",
    "occlusions": [
      "Robot body and arm obscure right-side player area and some chips/cards.",
      "Human hands obscure the top player's held cards."
    ]
  },
  "uncertainty": [
    "Exact chip counts and denominations are uncertain due to perspective, overlap, and occlusion.",
    "No face-up hole cards are visible.",
    "Active turn cannot be determined from this single image.",
    "Board interpretation is limited to three clearly exposed cards: 3C, 5D, 10C."
  ],
  "need_more_images": true
}
