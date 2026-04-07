#!/usr/bin/env python3
"""Dry run test: generate synthetic poker table images and run the full loop.

Renders poker scenes using Pillow (green table, card rectangles, colored chips,
robot arm indicator) and feeds them through route.py and executor.py --dry-run
to test the complete loop without physical hardware.

Usage:
    python3 src/dry_run.py                    # run full hand lifecycle
    python3 src/dry_run.py --output-dir /tmp/dryrun  # save images to custom dir
    python3 src/dry_run.py --render-only       # just generate images, no loop
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

# ── rendering constants ───────────────────────────────────────────────────

WIDTH, HEIGHT = 1280, 720
TABLE_COLOR = (34, 119, 59)  # green felt
CARD_W, CARD_H = 70, 100
CHIP_R = 18

SUIT_COLORS = {"h": (200, 30, 30), "d": (200, 30, 30), "c": (30, 30, 30), "s": (30, 30, 30)}
SUIT_SYMBOLS = {"h": "h", "d": "d", "c": "c", "s": "s"}

CHIP_COLORS = {
    5: (200, 50, 50),      # red
    10: (200, 100, 180),   # pink
    50: (50, 160, 80),     # green
    100: (90, 60, 40),     # brown
}

ROBOT_ARM_COLOR = (140, 140, 150)
DEALER_BTN_COLOR = (255, 255, 200)


def _get_font(size=20):
    """Get a font, falling back to default if no TTF available."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except (OSError, AttributeError):
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except (OSError, AttributeError):
            return ImageFont.load_default()


def _draw_card(draw, x, y, card_str, font):
    """Draw a single card at (x, y). card_str is e.g. 'Ks', '??', or 'XX' for face-down."""
    if card_str in ("??", "XX"):
        # Face-down card
        draw.rounded_rectangle([x, y, x + CARD_W, y + CARD_H], radius=6,
                               fill=(40, 60, 140), outline=(20, 30, 80), width=2)
        draw.text((x + CARD_W // 2, y + CARD_H // 2), "?",
                  fill=(180, 180, 220), font=font, anchor="mm")
    else:
        # Face-up card
        rank = card_str[:-1]
        suit = card_str[-1]
        color = SUIT_COLORS.get(suit, (30, 30, 30))
        symbol = SUIT_SYMBOLS.get(suit, "?")

        draw.rounded_rectangle([x, y, x + CARD_W, y + CARD_H], radius=6,
                               fill=(255, 255, 255), outline=(100, 100, 100), width=2)
        draw.text((x + 8, y + 6), rank, fill=color, font=font)
        draw.text((x + CARD_W // 2, y + CARD_H * 2 // 3), symbol,
                  fill=color, font=font, anchor="mm")


def _draw_chips(draw, x, y, chips, font_sm):
    """Draw chip stacks horizontally starting at (x, y)."""
    cx = x
    for chip in chips:
        val = chip["value"]
        count = chip["count"]
        color = CHIP_COLORS.get(val, (128, 128, 128))
        for _ in range(count):
            draw.ellipse([cx - CHIP_R, y - CHIP_R, cx + CHIP_R, y + CHIP_R],
                         fill=color, outline=(40, 40, 40), width=1)
            draw.text((cx, y), str(val), fill=(255, 255, 255), font=font_sm, anchor="mm")
            cx += CHIP_R * 2 + 4


def _draw_robot_arm(draw, robot_state, held_card, font):
    """Draw robot arm indicator on the right side."""
    arm_x = WIDTH - 120
    label_y = 300

    if robot_state == "idle":
        # Arm at rest position (right side, middle)
        draw.rounded_rectangle([arm_x, 320, arm_x + 80, 420], radius=4,
                               fill=ROBOT_ARM_COLOR, outline=(100, 100, 110))
        draw.text((arm_x + 40, label_y), "ARM: IDLE",
                  fill=(200, 200, 200), font=font, anchor="mm")

    elif robot_state == "moving":
        # Arm reaching down (angled)
        draw.polygon([(arm_x, 280), (arm_x + 80, 280),
                      (arm_x + 60, 420), (arm_x + 20, 420)],
                     fill=ROBOT_ARM_COLOR, outline=(100, 100, 110))
        draw.text((arm_x + 40, 260), "ARM: MOVING",
                  fill=(255, 200, 100), font=font, anchor="mm")

    elif robot_state == "holding_card":
        # Arm holding a card up
        draw.rounded_rectangle([arm_x, 200, arm_x + 80, 340], radius=4,
                               fill=ROBOT_ARM_COLOR, outline=(100, 100, 110))
        draw.text((arm_x + 40, 180), "HOLDING",
                  fill=(100, 255, 100), font=font, anchor="mm")
        if held_card:
            _draw_card(draw, arm_x + 5, 210, held_card, font)


def _draw_dealer_button(draw, x, y, font_sm):
    """Draw a dealer button."""
    draw.ellipse([x - 15, y - 15, x + 15, y + 15],
                 fill=DEALER_BTN_COLOR, outline=(180, 160, 80), width=2)
    draw.text((x, y), "D", fill=(40, 40, 40), font=font_sm, anchor="mm")


def render_scene(scene, output_path):
    """Render a poker table scene to an image file.

    Args:
        scene: dict with keys like community_cards, robot_cards, robot_state, etc.
        output_path: where to save the image

    Returns:
        output_path
    """
    img = Image.new("RGB", (WIDTH, HEIGHT), TABLE_COLOR)
    draw = ImageDraw.Draw(img)
    font = _get_font(20)
    font_lg = _get_font(28)
    font_sm = _get_font(14)

    # ── table outline ──
    draw.rounded_rectangle([30, 30, WIDTH - 30, HEIGHT - 30], radius=60,
                           outline=(20, 80, 40), width=4)

    # ── opponent area (top) ──
    opp_chips = scene.get("opponent_chips", [])
    opp_bet = scene.get("opponent_bet", [])
    # Opponent cards (always face down) — centered
    _draw_card(draw, 560, 60, "XX", font)
    _draw_card(draw, 640, 60, "XX", font)
    draw.text((600, 170), "Opponent", fill=(200, 200, 200), font=font_sm, anchor="mm")
    # Opponent chips on the right
    if opp_chips:
        _draw_chips(draw, WIDTH - 350, 80, opp_chips, font_sm)
    # Opponent bet on the right, below their stack
    if opp_bet:
        _draw_chips(draw, WIDTH - 250, 140, opp_bet, font_sm)

    # ── community cards (center) ──
    community = scene.get("community_cards", [])
    if community:
        start_x = (WIDTH - len(community) * (CARD_W + 12)) // 2
        for i, card in enumerate(community):
            _draw_card(draw, start_x + i * (CARD_W + 12), 280, card, font)
    else:
        draw.text((WIDTH // 2, 330), "[ no community cards ]",
                  fill=(100, 160, 100), font=font, anchor="mm")

    # ── pot chips (center below community) ──
    pot_chips = scene.get("pot_chips", [])
    if pot_chips:
        draw.text((WIDTH // 2, 400), "POT", fill=(200, 200, 200), font=font_sm, anchor="mm")
        _draw_chips(draw, WIDTH // 2 - 80, 420, pot_chips, font_sm)

    # ── robot area (bottom) ──
    robot_cards = scene.get("robot_cards", ["??", "??"])
    _draw_card(draw, 560, 530, robot_cards[0], font)
    _draw_card(draw, 640, 530, robot_cards[1], font)

    # Robot chips on the left
    my_chips = scene.get("my_chips", [])
    if my_chips:
        _draw_chips(draw, 80, 600, my_chips, font_sm)

    # Robot bet on the left, above their stack
    my_bet = scene.get("my_bet", [])
    if my_bet:
        _draw_chips(draw, 80, 550, my_bet, font_sm)

    # ── position & dealer button ──
    pos = scene.get("my_position", "CO")
    draw.text((560, 650), f"Position: {pos}", fill=(200, 200, 200), font=font_sm)

    dealer_seat = scene.get("dealer_seat", "BTN")
    if dealer_seat == "BTN":
        _draw_dealer_button(draw, 530, 560, font_sm)
    else:
        _draw_dealer_button(draw, 720, 80, font_sm)

    # ── robot arm ──
    _draw_robot_arm(draw, scene.get("robot_state", "idle"),
                    scene.get("held_card"), font)

    # ── turn indicator ──
    is_my_turn = scene.get("is_my_turn", False)
    game_phase = scene.get("game_phase", "active")
    to_call = scene.get("to_call", 0)

    status_text = f"Phase: {game_phase}"
    if is_my_turn:
        status_text += "  |  YOUR TURN"
    if to_call:
        status_text += f"  |  To call: {to_call}"
    draw.text((WIDTH // 2, HEIGHT - 15), status_text,
              fill=(220, 220, 220), font=font_sm, anchor="mm")

    # ── street label ──
    street_map = {0: "Pre-flop", 3: "Flop", 4: "Turn", 5: "River"}
    street = street_map.get(len(community), "")
    if street:
        draw.text((WIDTH // 2, 265), street, fill=(180, 220, 180), font=font_sm, anchor="mm")

    img.save(output_path)
    return output_path


# ── scenario definition ───────────────────────────────────────────────────

BASE_CHIPS = [{"value": 100, "count": 4}, {"value": 50, "count": 2}, {"value": 10, "count": 5}]
OPP_CHIPS = [{"value": 100, "count": 5}, {"value": 50, "count": 3}]

SCENARIO = [
    {
        "desc": "Preflop, idle, no community — should view left card",
        "scene": {
            "community_cards": [],
            "robot_cards": ["??", "??"],
            "robot_state": "idle",
            "held_card": None,
            "my_chips": BASE_CHIPS,
            "pot_chips": [{"value": 10, "count": 3}],
            "opponent_chips": OPP_CHIPS,
            "opponent_bet": [{"value": 10, "count": 1}],
            "my_bet": [{"value": 10, "count": 1}],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": True,
            "game_phase": "active",
            "to_call": 20,
        },
        "mock_action": None,  # route should hint view_card
    },
    {
        "desc": "Robot moving (viewing left card)",
        "scene": {
            "community_cards": [],
            "robot_cards": ["??", "??"],
            "robot_state": "moving",
            "held_card": None,
            "my_chips": BASE_CHIPS,
            "pot_chips": [{"value": 10, "count": 3}],
            "opponent_chips": OPP_CHIPS,
            "opponent_bet": [{"value": 10, "count": 1}],
            "my_bet": [{"value": 10, "count": 1}],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": True,
            "game_phase": "active",
            "to_call": 20,
        },
        "mock_action": None,
    },
    {
        "desc": "Robot holding left card (Ks)",
        "scene": {
            "community_cards": [],
            "robot_cards": ["??", "??"],
            "robot_state": "holding_card",
            "held_card": "Ks",
            "my_chips": BASE_CHIPS,
            "pot_chips": [{"value": 10, "count": 3}],
            "opponent_chips": OPP_CHIPS,
            "opponent_bet": [{"value": 10, "count": 1}],
            "my_bet": [{"value": 10, "count": 1}],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": True,
            "game_phase": "active",
            "to_call": 20,
        },
        "mock_action": None,  # route should hint put_down_card
    },
    {
        "desc": "Idle again, left cached — should view right card",
        "scene": {
            "community_cards": [],
            "robot_cards": ["??", "??"],
            "robot_state": "idle",
            "held_card": None,
            "my_chips": BASE_CHIPS,
            "pot_chips": [{"value": 10, "count": 3}],
            "opponent_chips": OPP_CHIPS,
            "opponent_bet": [{"value": 10, "count": 1}],
            "my_bet": [{"value": 10, "count": 1}],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": True,
            "game_phase": "active",
            "to_call": 20,
        },
        "mock_action": None,
    },
    {
        "desc": "Robot moving (viewing right card)",
        "scene": {
            "community_cards": [],
            "robot_cards": ["??", "??"],
            "robot_state": "moving",
            "held_card": None,
            "my_chips": BASE_CHIPS,
            "pot_chips": [{"value": 10, "count": 3}],
            "opponent_chips": OPP_CHIPS,
            "opponent_bet": [{"value": 10, "count": 1}],
            "my_bet": [{"value": 10, "count": 1}],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": True,
            "game_phase": "active",
            "to_call": 20,
        },
        "mock_action": None,
    },
    {
        "desc": "Robot holding right card (Qh) — hand complete",
        "scene": {
            "community_cards": [],
            "robot_cards": ["??", "??"],
            "robot_state": "holding_card",
            "held_card": "Qh",
            "my_chips": BASE_CHIPS,
            "pot_chips": [{"value": 10, "count": 3}],
            "opponent_chips": OPP_CHIPS,
            "opponent_bet": [{"value": 10, "count": 1}],
            "my_bet": [{"value": 10, "count": 1}],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": True,
            "game_phase": "active",
            "to_call": 20,
        },
        "mock_action": {"action": "call", "bet_chips": 20},
    },
    {
        "desc": "Flop [7h, 9c, 3s], my turn",
        "scene": {
            "community_cards": ["7h", "9c", "3s"],
            "robot_cards": ["??", "??"],
            "robot_state": "idle",
            "held_card": None,
            "my_chips": [{"value": 100, "count": 4}, {"value": 50, "count": 2}, {"value": 10, "count": 3}],
            "pot_chips": [{"value": 10, "count": 7}],
            "opponent_chips": [{"value": 100, "count": 5}, {"value": 50, "count": 2}],
            "opponent_bet": [],
            "my_bet": [],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": True,
            "game_phase": "active",
            "to_call": 0,
        },
        "mock_action": {"action": "check"},
    },
    {
        "desc": "Turn [7h, 9c, 3s, Jd], not my turn",
        "scene": {
            "community_cards": ["7h", "9c", "3s", "Jd"],
            "robot_cards": ["??", "??"],
            "robot_state": "idle",
            "held_card": None,
            "my_chips": [{"value": 100, "count": 4}, {"value": 50, "count": 2}, {"value": 10, "count": 3}],
            "pot_chips": [{"value": 10, "count": 7}],
            "opponent_chips": [{"value": 100, "count": 5}, {"value": 50, "count": 2}],
            "opponent_bet": [],
            "my_bet": [],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": False,
            "game_phase": "active",
            "to_call": 0,
        },
        "mock_action": None,
    },
    {
        "desc": "Turn, my turn now",
        "scene": {
            "community_cards": ["7h", "9c", "3s", "Jd"],
            "robot_cards": ["??", "??"],
            "robot_state": "idle",
            "held_card": None,
            "my_chips": [{"value": 100, "count": 4}, {"value": 50, "count": 2}, {"value": 10, "count": 3}],
            "pot_chips": [{"value": 10, "count": 7}, {"value": 50, "count": 1}],
            "opponent_chips": [{"value": 100, "count": 5}, {"value": 50, "count": 1}],
            "opponent_bet": [{"value": 50, "count": 1}],
            "my_bet": [],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": True,
            "game_phase": "active",
            "to_call": 50,
        },
        "mock_action": {"action": "raise", "bet_chips": 150, "amount": 150},
    },
    {
        "desc": "Between hands",
        "scene": {
            "community_cards": ["7h", "9c", "3s", "Jd", "2d"],
            "robot_cards": ["??", "??"],
            "robot_state": "idle",
            "held_card": None,
            "my_chips": [{"value": 100, "count": 5}, {"value": 50, "count": 3}, {"value": 10, "count": 3}],
            "pot_chips": [],
            "opponent_chips": [{"value": 100, "count": 4}, {"value": 50, "count": 1}],
            "opponent_bet": [],
            "my_bet": [],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": False,
            "game_phase": "between_hands",
            "to_call": 0,
        },
        "mock_action": None,
    },
    {
        "desc": "Game over",
        "scene": {
            "community_cards": [],
            "robot_cards": ["??", "??"],
            "robot_state": "idle",
            "held_card": None,
            "my_chips": [{"value": 100, "count": 5}, {"value": 50, "count": 3}, {"value": 10, "count": 3}],
            "pot_chips": [],
            "opponent_chips": [],
            "opponent_bet": [],
            "my_bet": [],
            "my_position": "CO",
            "dealer_seat": "BTN",
            "is_my_turn": False,
            "game_phase": "game_over",
            "to_call": 0,
        },
        "mock_action": None,
    },
]


# ── loop runner ───────────────────────────────────────────────────────────

def _run_script(script, *args):
    """Run a src/ script and return (stdout, returncode)."""
    cmd = [sys.executable, os.path.join(SRC_DIR, script)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=SKILL_DIR)
    return result.stdout.strip(), result.returncode


def run_loop(output_dir, render_only=False):
    """Run the dry run loop through all scenario steps."""
    os.makedirs(output_dir, exist_ok=True)

    # Init experiment
    if not render_only:
        stdout, _ = _run_script("execution_state.py", "init")
        print(f"Experiment init: {stdout}")

    prev_image = None

    for i, step in enumerate(SCENARIO):
        step_num = i + 1
        desc = step["desc"]
        scene = step["scene"]
        mock_action = step.get("mock_action")

        print(f"\n{'='*60}")
        print(f"Step {step_num}: {desc}")
        print(f"{'='*60}")

        # 1. ENV — render scene
        image_path = os.path.join(output_dir, f"step_{step_num:02d}.jpg")
        render_scene(scene, image_path)
        print(f"  ENV:    rendered {image_path}")

        if render_only:
            prev_image = image_path
            continue

        # Save frame
        _run_script("execution_state.py", "save-frame", image_path,
                     "--round", str(step_num), "--label", "capture")

        # 2. VISION — skipped in dry run, use scene directly as game state
        # (The real loop would have the vision model read the image)
        game_state = {
            "hand": [],
            "held_card": scene.get("held_card"),
            "robot_state": scene.get("robot_state", "idle"),
            "community_cards": scene.get("community_cards", []),
            "street": {0: "preflop", 3: "flop", 4: "turn", 5: "river"}.get(
                len(scene.get("community_cards", [])), "preflop"),
            "my_chips": scene.get("my_chips", []),
            "players": [{"seat": "BTN", "chips": scene.get("opponent_chips", []),
                         "status": "active", "current_bet": scene.get("opponent_bet", [])}],
            "pot_chips": scene.get("pot_chips", []),
            "my_current_bet": scene.get("my_bet", []),
            "to_call": scene.get("to_call", 0),
            "my_position": scene.get("my_position", "CO"),
            "blinds": {"small": 5, "big": 10},
            "vision_confidence": 0.95,
            "uncertain_fields": [],
            "is_my_turn": scene.get("is_my_turn", False),
            "game_phase": scene.get("game_phase", "active"),
            "action_prompt": ["fold", "call", "raise"] if scene.get("is_my_turn") else [],
            "scene_stable": True,
        }
        print(f"  VISION: game_phase={game_state['game_phase']}, "
              f"robot={game_state['robot_state']}, turn={game_state['is_my_turn']}")

        # 3. ROUTE
        state_json = json.dumps(game_state)
        stdout, rc = _run_script("route.py", "--state", state_json)
        if rc != 0:
            print(f"  ROUTE:  ERROR (rc={rc}): {stdout}")
            continue

        route_result = json.loads(stdout)
        next_action = route_result.get("next")
        print(f"  ROUTE:  {json.dumps(route_result, indent=None)}")

        # 4. Handle routing
        if next_action == "stop":
            print(f"  ACTION: STOP — loop ends")
            break

        elif next_action == "wait":
            reason = route_result.get("reason", "unknown")
            print(f"  ACTION: WAIT ({reason}) — sleep and recapture")

        elif next_action == "resume":
            print(f"  ACTION: RESUME — cancelling previous execution")
            stdout, _ = _run_script("executor.py", "--cancel-previous")
            print(f"  EXEC:   {stdout}")

        elif next_action == "reason":
            hint = route_result.get("action_hint")
            hand = route_result.get("hand")

            if hint:
                # Mechanical action — use hint directly
                if hint == "view_card":
                    pos = route_result.get("position", "left")
                    action = {"action": "view_card", "position": pos}
                elif hint == "put_down_card":
                    action = {"action": "put_down_card"}
                else:
                    action = {"action": hint}
                print(f"  REASON: action_hint={hint} (no poker reasoning needed)")
            elif mock_action:
                # Use pre-defined mock action
                action = mock_action
                print(f"  REASON: mock action={json.dumps(action)}"
                      f"  (hand={hand})")
            else:
                print(f"  REASON: would reason with hand={hand}, skipping (no mock action)")
                continue

            # 5. EXECUTE (dry run)
            exec_args = ["--action", json.dumps(action), "--dry-run"]
            chips = game_state.get("my_chips")
            if chips:
                exec_args += ["--chips", json.dumps(chips)]
            stdout, rc = _run_script("executor.py", *exec_args)
            print(f"  EXEC:   {stdout}")

        prev_image = image_path

    print(f"\n{'='*60}")
    print(f"Dry run complete. Images saved to {output_dir}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Dry run test: generate synthetic poker images and run the loop.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to save rendered images (default: temp dir)",
    )
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="Only render images, don't run the loop",
    )
    args = parser.parse_args()

    output_dir = args.output_dir or tempfile.mkdtemp(prefix="dexholdem_dryrun_")
    run_loop(output_dir, render_only=args.render_only)


if __name__ == "__main__":
    main()
