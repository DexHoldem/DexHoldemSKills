#!/usr/bin/env python3
"""Poker game simulator for testing the dexholdem loop without hardware.

Manages a heads-up Texas Hold'em game: deck, chips (denomination-level),
community cards, blinds, and opponent AI. Renders scenes as images and
exports game state compatible with route.py.

Usage:
    python3 simulator.py                          # interactive mode
    python3 simulator.py --auto                   # auto-play with random robot
    python3 simulator.py render /tmp/frame.jpg    # render current state
    python3 simulator.py apply '{"action":"call","bet_chips":10}'
    python3 simulator.py state                    # print game state JSON
"""

import argparse
import itertools
import json
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

# ── rendering constants (from dry_run.py) ─────────────────────────────────

WIDTH, HEIGHT = 1280, 720
TABLE_COLOR = (34, 119, 59)
CARD_W, CARD_H = 70, 100
CHIP_R = 18

SUIT_COLORS = {"h": (200, 30, 30), "d": (200, 30, 30),
               "c": (30, 30, 30), "s": (30, 30, 30)}
SUIT_SYMBOLS = {"h": "h", "d": "d", "c": "c", "s": "s"}

CHIP_COLORS = {
    5: (200, 50, 50),      # red
    10: (200, 100, 180),   # pink
    50: (50, 160, 80),     # green
    100: (90, 60, 40),     # brown
}

ROBOT_ARM_COLOR = (140, 140, 150)
DEALER_BTN_COLOR = (255, 255, 200)

# ── poker constants ───────────────────────────────────────────────────────

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
SUITS = ["h", "d", "c", "s"]
RANK_VALUES = {r: i for i, r in enumerate(RANKS, 2)}  # 2=2 .. A=14

DENOMS = [5, 10, 50, 100]
STARTING_COUNT = 4  # 4 chips per denomination per player
SMALL_BLIND = 5
BIG_BLIND = 10

# hand ranking categories (higher = better)
HIGH_CARD, ONE_PAIR, TWO_PAIR, THREE_KIND = 0, 1, 2, 3
STRAIGHT, FLUSH, FULL_HOUSE, FOUR_KIND = 4, 5, 6, 7
STRAIGHT_FLUSH, ROYAL_FLUSH = 8, 9


# ── rendering functions (from dry_run.py) ─────────────────────────────────

def _get_font(size=20):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except (OSError, AttributeError):
        try:
            return ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except (OSError, AttributeError):
            return ImageFont.load_default()


def _draw_card(draw, x, y, card_str, font):
    if card_str in ("??", "XX"):
        draw.rounded_rectangle([x, y, x + CARD_W, y + CARD_H], radius=6,
                               fill=(40, 60, 140), outline=(20, 30, 80), width=2)
        draw.text((x + CARD_W // 2, y + CARD_H // 2), "?",
                  fill=(180, 180, 220), font=font, anchor="mm")
    else:
        rank, suit = card_str[:-1], card_str[-1]
        color = SUIT_COLORS.get(suit, (30, 30, 30))
        symbol = SUIT_SYMBOLS.get(suit, "?")
        draw.rounded_rectangle([x, y, x + CARD_W, y + CARD_H], radius=6,
                               fill=(255, 255, 255), outline=(100, 100, 100), width=2)
        draw.text((x + 8, y + 6), rank, fill=color, font=font)
        draw.text((x + CARD_W // 2, y + CARD_H * 2 // 3), symbol,
                  fill=color, font=font, anchor="mm")


def _draw_chips(draw, x, y, chips, font_sm):
    cx = x
    for chip in chips:
        val, count = chip["value"], chip["count"]
        color = CHIP_COLORS.get(val, (128, 128, 128))
        for _ in range(count):
            draw.ellipse([cx - CHIP_R, y - CHIP_R, cx + CHIP_R, y + CHIP_R],
                         fill=color, outline=(40, 40, 40), width=1)
            draw.text((cx, y), str(val), fill=(255, 255, 255),
                      font=font_sm, anchor="mm")
            cx += CHIP_R * 2 + 4


def _draw_robot_arm(draw, robot_state, held_card, font):
    arm_x = WIDTH - 120
    if robot_state == "idle":
        draw.rounded_rectangle([arm_x, 320, arm_x + 80, 420], radius=4,
                               fill=ROBOT_ARM_COLOR, outline=(100, 100, 110))
        draw.text((arm_x + 40, 300), "ARM: IDLE",
                  fill=(200, 200, 200), font=font, anchor="mm")
    elif robot_state == "moving":
        draw.polygon([(arm_x, 280), (arm_x + 80, 280),
                      (arm_x + 60, 420), (arm_x + 20, 420)],
                     fill=ROBOT_ARM_COLOR, outline=(100, 100, 110))
        draw.text((arm_x + 40, 260), "ARM: MOVING",
                  fill=(255, 200, 100), font=font, anchor="mm")
    elif robot_state == "holding_card":
        draw.rounded_rectangle([arm_x, 200, arm_x + 80, 340], radius=4,
                               fill=ROBOT_ARM_COLOR, outline=(100, 100, 110))
        draw.text((arm_x + 40, 180), "HOLDING",
                  fill=(100, 255, 100), font=font, anchor="mm")
        if held_card:
            _draw_card(draw, arm_x + 5, 210, held_card, font)


def _draw_dealer_button(draw, x, y, font_sm):
    draw.ellipse([x - 15, y - 15, x + 15, y + 15],
                 fill=DEALER_BTN_COLOR, outline=(180, 160, 80), width=2)
    draw.text((x, y), "D", fill=(40, 40, 40), font=font_sm, anchor="mm")


def render_scene(scene, output_path):
    """Render a poker table scene to an image file."""
    img = Image.new("RGB", (WIDTH, HEIGHT), TABLE_COLOR)
    draw = ImageDraw.Draw(img)
    font = _get_font(20)
    font_sm = _get_font(14)

    # table outline
    draw.rounded_rectangle([30, 30, WIDTH - 30, HEIGHT - 30], radius=60,
                           outline=(20, 80, 40), width=4)

    # opponent area (top)
    opp_chips = scene.get("opponent_chips", [])
    opp_bet = scene.get("opponent_bet", [])
    _draw_card(draw, 560, 60, "XX", font)
    _draw_card(draw, 640, 60, "XX", font)
    draw.text((600, 170), "Opponent", fill=(200, 200, 200),
              font=font_sm, anchor="mm")
    if opp_chips:
        _draw_chips(draw, WIDTH - 350, 80, opp_chips, font_sm)
    if opp_bet:
        _draw_chips(draw, WIDTH - 250, 140, opp_bet, font_sm)

    # community cards (center)
    community = scene.get("community_cards", [])
    if community:
        start_x = (WIDTH - len(community) * (CARD_W + 12)) // 2
        for i, card in enumerate(community):
            _draw_card(draw, start_x + i * (CARD_W + 12), 280, card, font)
    else:
        draw.text((WIDTH // 2, 330), "[ no community cards ]",
                  fill=(100, 160, 100), font=font, anchor="mm")

    # pot chips
    pot_chips = scene.get("pot_chips", [])
    if pot_chips:
        draw.text((WIDTH // 2, 400), "POT", fill=(200, 200, 200),
                  font=font_sm, anchor="mm")
        _draw_chips(draw, WIDTH // 2 - 80, 420, pot_chips, font_sm)

    # robot area (bottom)
    robot_cards = scene.get("robot_cards", ["??", "??"])
    _draw_card(draw, 560, 530, robot_cards[0], font)
    _draw_card(draw, 640, 530, robot_cards[1], font)

    my_chips = scene.get("my_chips", [])
    if my_chips:
        _draw_chips(draw, 80, 600, my_chips, font_sm)

    my_bet = scene.get("my_bet", [])
    if my_bet:
        _draw_chips(draw, 80, 550, my_bet, font_sm)

    # position & dealer button
    pos = scene.get("my_position", "")
    draw.text((560, 650), f"Position: {pos}", fill=(200, 200, 200),
              font=font_sm)

    dealer_seat = scene.get("dealer_seat", "BTN")
    if dealer_seat == "BTN":
        _draw_dealer_button(draw, 530, 560, font_sm)
    else:
        _draw_dealer_button(draw, 720, 80, font_sm)

    # robot arm
    _draw_robot_arm(draw, scene.get("robot_state", "idle"),
                    scene.get("held_card"), font)

    # status bar
    is_my_turn = scene.get("is_my_turn", False)
    game_phase = scene.get("game_phase", "active")
    to_call = scene.get("to_call", 0)
    status = f"Phase: {game_phase}"
    if is_my_turn:
        status += "  |  YOUR TURN"
    if to_call:
        status += f"  |  To call: {to_call}"
    draw.text((WIDTH // 2, HEIGHT - 15), status,
              fill=(220, 220, 220), font=font_sm, anchor="mm")

    # street label
    street_map = {0: "Pre-flop", 3: "Flop", 4: "Turn", 5: "River"}
    street = street_map.get(len(community), "")
    if street:
        draw.text((WIDTH // 2, 265), street, fill=(180, 220, 180),
                  font=font_sm, anchor="mm")

    img.save(output_path)
    return output_path


# ── chip stack ────────────────────────────────────────────────────────────

class ChipStack:
    """Denomination-level chip tracking."""

    def __init__(self, counts=None):
        # counts: {value: count}
        self._chips = {d: 0 for d in DENOMS}
        if counts:
            for d, c in counts.items():
                self._chips[int(d)] = c

    @classmethod
    def starting(cls):
        return cls({d: STARTING_COUNT for d in DENOMS})

    @classmethod
    def from_list(cls, lst):
        cs = cls()
        for item in lst:
            cs._chips[item["value"]] = item["count"]
        return cs

    def to_list(self):
        return [{"value": d, "count": c}
                for d, c in sorted(self._chips.items(), reverse=True) if c > 0]

    def total(self):
        return sum(d * c for d, c in self._chips.items())

    def is_empty(self):
        return self.total() == 0

    def remove(self, amount):
        """Remove chips totalling amount (greedy largest-first). Returns ChipStack removed."""
        removed = ChipStack()
        remaining = amount
        for d in sorted(self._chips.keys(), reverse=True):
            if remaining <= 0:
                break
            use = min(self._chips[d], remaining // d)
            if use > 0:
                removed._chips[d] = use
                self._chips[d] -= use
                remaining -= use * d

        if remaining > 0:
            # overpay with smallest chip that covers remainder
            for d in sorted(self._chips.keys()):
                if self._chips[d] > 0 and d >= remaining:
                    removed._chips[d] = removed._chips.get(d, 0) + 1
                    self._chips[d] -= 1
                    remaining = 0
                    break
            if remaining > 0:
                # last resort: any available chip
                for d in sorted(self._chips.keys(), reverse=True):
                    if self._chips[d] > 0:
                        removed._chips[d] = removed._chips.get(d, 0) + 1
                        self._chips[d] -= 1
                        remaining = 0
                        break

        return removed

    def remove_all(self):
        """Remove all chips, return them as a new ChipStack."""
        removed = ChipStack(dict(self._chips))
        self._chips = {d: 0 for d in DENOMS}
        return removed

    def add(self, other):
        for d in DENOMS:
            self._chips[d] += other._chips.get(d, 0)

    def copy(self):
        return ChipStack(dict(self._chips))

    def __repr__(self):
        parts = [f"{d}×{c}" for d, c in sorted(self._chips.items()) if c > 0]
        return f"ChipStack({', '.join(parts) or 'empty'}, total={self.total()})"


# ── deck ──────────────────────────────────────────────────────────────────

def make_deck():
    return [r + s for r in RANKS for s in SUITS]


# ── hand evaluator ────────────────────────────────────────────────────────

def _hand_rank(five_cards):
    """Rank a 5-card hand. Returns a tuple for comparison (higher = better)."""
    ranks = sorted([RANK_VALUES[c[:-1]] for c in five_cards], reverse=True)
    suits = [c[-1] for c in five_cards]

    is_flush = len(set(suits)) == 1
    is_straight = False
    straight_high = 0

    # check straight
    if ranks[0] - ranks[4] == 4 and len(set(ranks)) == 5:
        is_straight = True
        straight_high = ranks[0]
    # ace-low straight (A-2-3-4-5)
    elif ranks == [14, 5, 4, 3, 2]:
        is_straight = True
        straight_high = 5  # 5-high straight

    # count rank frequencies
    from collections import Counter
    freq = Counter(ranks)
    groups = sorted(freq.items(), key=lambda x: (x[1], x[0]), reverse=True)

    if is_straight and is_flush:
        if straight_high == 14:
            return (ROYAL_FLUSH, 14)
        return (STRAIGHT_FLUSH, straight_high)
    if groups[0][1] == 4:
        return (FOUR_KIND, groups[0][0], groups[1][0])
    if groups[0][1] == 3 and groups[1][1] == 2:
        return (FULL_HOUSE, groups[0][0], groups[1][0])
    if is_flush:
        return (FLUSH,) + tuple(ranks)
    if is_straight:
        return (STRAIGHT, straight_high)
    if groups[0][1] == 3:
        kickers = sorted([r for r, c in groups if c == 1], reverse=True)
        return (THREE_KIND, groups[0][0]) + tuple(kickers)
    if groups[0][1] == 2 and groups[1][1] == 2:
        pairs = sorted([r for r, c in groups if c == 2], reverse=True)
        kicker = [r for r, c in groups if c == 1][0]
        return (TWO_PAIR, pairs[0], pairs[1], kicker)
    if groups[0][1] == 2:
        kickers = sorted([r for r, c in groups if c == 1], reverse=True)
        return (ONE_PAIR, groups[0][0]) + tuple(kickers)
    return (HIGH_CARD,) + tuple(ranks)


def best_hand(hole_cards, community_cards):
    """Find best 5-card hand from 7 cards. Returns rank tuple."""
    all_cards = list(hole_cards) + list(community_cards)
    if len(all_cards) < 5:
        # not enough cards for a full hand (shouldn't happen at showdown)
        return (HIGH_CARD, 0)
    best = None
    for combo in itertools.combinations(all_cards, 5):
        rank = _hand_rank(list(combo))
        if best is None or rank > best:
            best = rank
    return best


HAND_NAMES = {
    HIGH_CARD: "High Card", ONE_PAIR: "One Pair", TWO_PAIR: "Two Pair",
    THREE_KIND: "Three of a Kind", STRAIGHT: "Straight", FLUSH: "Flush",
    FULL_HOUSE: "Full House", FOUR_KIND: "Four of a Kind",
    STRAIGHT_FLUSH: "Straight Flush", ROYAL_FLUSH: "Royal Flush",
}


# ── player ────────────────────────────────────────────────────────────────

class Player:
    def __init__(self, name):
        self.name = name
        self.chips = ChipStack.starting()
        self.hole_cards = []
        self.current_bet = ChipStack()
        self.folded = False
        self.is_all_in = False
        self.street_invested = 0  # total chips put in this street

    def reset_for_hand(self):
        self.hole_cards = []
        self.current_bet = ChipStack()
        self.folded = False
        self.is_all_in = False
        self.street_invested = 0

    def reset_street(self):
        self.current_bet = ChipStack()
        self.street_invested = 0


# ── simulator ─────────────────────────────────────────────────────────────

class PokerSimulator:
    def __init__(self):
        self.robot = Player("Robot")
        self.opponent = Player("Opponent")
        self.deck = []
        self.community_cards = []
        self.pot = ChipStack()
        self.street = "preflop"
        self.dealer = "robot"  # alternates each hand
        self.robot_state = "idle"
        self.held_card = None
        self.hand_cache = {"left": None, "right": None}
        self.is_robot_turn = True
        self.game_phase = "waiting"  # waiting, active, between_hands, showdown, game_over
        self.hand_number = 0
        self.action_log = []
        self._opp_acted_this_street = False
        self._robot_acted_this_street = False

    def new_hand(self):
        """Deal a new hand."""
        self.hand_number += 1
        self.robot.reset_for_hand()
        self.opponent.reset_for_hand()
        self.pot = ChipStack()
        self.community_cards = []
        self.street = "preflop"
        self.robot_state = "idle"
        self.held_card = None
        self.hand_cache = {"left": None, "right": None}
        self.game_phase = "active"
        self.action_log = []
        self._opp_acted_this_street = False
        self._robot_acted_this_street = False

        # check if either player is busted
        if self.robot.chips.is_empty() or self.opponent.chips.is_empty():
            self.game_phase = "game_over"
            return

        # alternate dealer
        if self.hand_number > 1:
            self.dealer = "opponent" if self.dealer == "robot" else "robot"

        # shuffle and deal
        self.deck = make_deck()
        random.shuffle(self.deck)
        self.robot.hole_cards = [self.deck.pop(), self.deck.pop()]
        self.opponent.hole_cards = [self.deck.pop(), self.deck.pop()]

        # post blinds — in heads-up, dealer=SB, non-dealer=BB
        if self.dealer == "robot":
            sb_player, bb_player = self.robot, self.opponent
        else:
            sb_player, bb_player = self.opponent, self.robot

        sb_chips = sb_player.chips.remove(SMALL_BLIND)
        sb_player.current_bet.add(sb_chips)
        sb_player.street_invested = SMALL_BLIND

        bb_chips = bb_player.chips.remove(BIG_BLIND)
        bb_player.current_bet.add(bb_chips)
        bb_player.street_invested = BIG_BLIND

        # preflop: dealer/SB acts first
        self.is_robot_turn = (self.dealer == "robot")

        # if opponent acts first preflop, let them act
        if not self.is_robot_turn:
            self._opponent_act()

    def _compute_to_call(self):
        opp_invested = self.opponent.street_invested
        robot_invested = self.robot.street_invested
        return max(0, opp_invested - robot_invested)

    def _valid_actions(self):
        actions = []
        to_call = self._compute_to_call()
        if to_call > 0:
            actions.extend(["fold", "call", "raise"])
        else:
            actions.extend(["check", "raise"])
        if not self.robot.chips.is_empty():
            actions.append("all_in")
        return actions

    def apply_action(self, action_obj):
        """Process a robot action. Returns result dict."""
        action = action_obj.get("action")
        self.action_log.append(action_obj)

        if action == "view_card":
            pos = action_obj.get("position", "left")
            idx = 0 if pos == "left" else 1
            card = self.robot.hole_cards[idx] if idx < len(self.robot.hole_cards) else None
            self.robot_state = "holding_card"
            self.held_card = card
            self.hand_cache[pos] = card
            return {"status": "ok", "held_card": card}

        if action == "put_down_card":
            self.robot_state = "idle"
            self.held_card = None
            return {"status": "ok"}

        if action == "fold":
            self.robot.folded = True
            # opponent wins pot + all current bets
            self.opponent.chips.add(self.pot)
            self.opponent.chips.add(self.robot.current_bet)
            self.opponent.chips.add(self.opponent.current_bet)
            self.pot = ChipStack()
            self.robot.current_bet = ChipStack()
            self.opponent.current_bet = ChipStack()
            self.game_phase = "between_hands"
            self.is_robot_turn = False
            return {"status": "ok", "result": "robot_folded"}

        if action == "check":
            self._robot_acted_this_street = True
            if self._opp_acted_this_street:
                # both acted, advance street
                self._advance_street()
            else:
                # opponent's turn
                self.is_robot_turn = False
                self._opponent_act()
                # after opponent acts, check if street should advance
                if self._street_complete():
                    self._advance_street()
            return {"status": "ok"}

        if action == "call":
            to_call = self._compute_to_call()
            actual = min(to_call, self.robot.chips.total())
            removed = self.robot.chips.remove(actual)
            self.robot.current_bet.add(removed)
            self.robot.street_invested += actual
            self._robot_acted_this_street = True
            if self.robot.chips.is_empty():
                self.robot.is_all_in = True
            # call completes the street action
            self._advance_street()
            return {"status": "ok", "called": actual}

        if action == "raise":
            bet_chips = action_obj.get("bet_chips", 0)
            # bet_chips is total amount robot puts in this street
            already_in = self.robot.street_invested
            additional = bet_chips - already_in
            actual = min(additional, self.robot.chips.total())
            removed = self.robot.chips.remove(actual)
            self.robot.current_bet.add(removed)
            self.robot.street_invested += actual
            self._robot_acted_this_street = True
            if self.robot.chips.is_empty():
                self.robot.is_all_in = True
            # opponent must respond
            self.is_robot_turn = False
            self._opponent_act()
            if self._street_complete():
                self._advance_street()
            return {"status": "ok", "raised_to": self.robot.street_invested}

        if action == "all_in":
            removed = self.robot.chips.remove_all()
            amount = removed.total()
            self.robot.current_bet.add(removed)
            self.robot.street_invested += amount
            self.robot.is_all_in = True
            self._robot_acted_this_street = True
            # opponent must respond
            self.is_robot_turn = False
            self._opponent_act()
            if self._street_complete():
                self._advance_street()
            return {"status": "ok", "all_in": amount}

        return {"status": "error", "message": f"unknown action: {action}"}

    def _street_complete(self):
        """Check if both players have acted and bets are equal (or all-in)."""
        if self.robot.folded or self.opponent.folded:
            return True
        if not self._robot_acted_this_street or not self._opp_acted_this_street:
            return False
        if self.robot.is_all_in or self.opponent.is_all_in:
            return True
        return self.robot.street_invested == self.opponent.street_invested

    def _advance_street(self):
        """Collect bets into pot, deal community cards, reset for next street."""
        # collect bets
        self.pot.add(self.robot.current_bet)
        self.pot.add(self.opponent.current_bet)
        self.robot.reset_street()
        self.opponent.reset_street()
        self._robot_acted_this_street = False
        self._opp_acted_this_street = False

        # if someone folded, hand is over
        if self.robot.folded or self.opponent.folded:
            return

        # if both all-in, deal remaining community and showdown
        if self.robot.is_all_in and self.opponent.is_all_in:
            while len(self.community_cards) < 5:
                self.community_cards.append(self.deck.pop())
            self._showdown()
            return

        if self.street == "preflop":
            self.street = "flop"
            for _ in range(3):
                self.community_cards.append(self.deck.pop())
        elif self.street == "flop":
            self.street = "turn"
            self.community_cards.append(self.deck.pop())
        elif self.street == "turn":
            self.street = "river"
            self.community_cards.append(self.deck.pop())
        elif self.street == "river":
            self._showdown()
            return

        # post-flop: non-dealer acts first
        # if one player is all-in, just advance to next street
        if self.robot.is_all_in or self.opponent.is_all_in:
            self._advance_street()
            return

        if self.dealer == "robot":
            # opponent (BB/non-dealer) acts first post-flop
            self.is_robot_turn = False
            self._opponent_act()
            if self._street_complete():
                self._advance_street()
            else:
                self.is_robot_turn = True
        else:
            # robot (non-dealer) acts first post-flop
            self.is_robot_turn = True

    def _showdown(self):
        """Evaluate hands and award pot."""
        self.game_phase = "showdown"

        robot_rank = best_hand(self.robot.hole_cards, self.community_cards)
        opp_rank = best_hand(self.opponent.hole_cards, self.community_cards)

        if robot_rank > opp_rank:
            self.robot.chips.add(self.pot)
            winner = "robot"
        elif opp_rank > robot_rank:
            self.opponent.chips.add(self.pot)
            winner = "opponent"
        else:
            # split pot — give half to each (may lose a chip to rounding)
            half = self.pot.total() // 2
            robot_share = self.pot.remove(half)
            self.robot.chips.add(robot_share)
            self.opponent.chips.add(self.pot)
            winner = "split"

        self.pot = ChipStack()
        self.game_phase = "between_hands"
        self.is_robot_turn = False

        self.action_log.append({
            "event": "showdown",
            "robot_hand": HAND_NAMES.get(robot_rank[0], "?"),
            "opponent_hand": HAND_NAMES.get(opp_rank[0], "?"),
            "winner": winner,
        })

    def _opponent_act(self):
        """Simple opponent AI."""
        if self.opponent.folded or self.opponent.is_all_in:
            self._opp_acted_this_street = True
            return

        to_call = max(0, self.robot.street_invested - self.opponent.street_invested)

        if to_call > 0:
            # facing a bet
            r = random.random()
            if r < 0.10:
                # fold
                self.opponent.folded = True
                self.robot.chips.add(self.pot)
                self.robot.chips.add(self.robot.current_bet)
                self.robot.chips.add(self.opponent.current_bet)
                self.pot = ChipStack()
                self.robot.current_bet = ChipStack()
                self.opponent.current_bet = ChipStack()
                self.game_phase = "between_hands"
                self.is_robot_turn = False
            elif r < 0.80:
                # call
                actual = min(to_call, self.opponent.chips.total())
                removed = self.opponent.chips.remove(actual)
                self.opponent.current_bet.add(removed)
                self.opponent.street_invested += actual
                if self.opponent.chips.is_empty():
                    self.opponent.is_all_in = True
            else:
                # raise (min-raise: double the bet)
                call_amount = min(to_call, self.opponent.chips.total())
                removed = self.opponent.chips.remove(call_amount)
                self.opponent.current_bet.add(removed)
                self.opponent.street_invested += call_amount
                # raise additional
                raise_add = min(to_call, self.opponent.chips.total())
                if raise_add > 0:
                    removed2 = self.opponent.chips.remove(raise_add)
                    self.opponent.current_bet.add(removed2)
                    self.opponent.street_invested += raise_add
                if self.opponent.chips.is_empty():
                    self.opponent.is_all_in = True
                # robot must respond
                self.is_robot_turn = True
        else:
            # no bet to call
            r = random.random()
            if r < 0.60:
                # check
                pass
            else:
                # bet (small: big blind amount)
                bet_amount = min(BIG_BLIND, self.opponent.chips.total())
                removed = self.opponent.chips.remove(bet_amount)
                self.opponent.current_bet.add(removed)
                self.opponent.street_invested += bet_amount
                if self.opponent.chips.is_empty():
                    self.opponent.is_all_in = True
                # robot must respond
                self.is_robot_turn = True

        self._opp_acted_this_street = True

    def get_game_state(self):
        """Export game state compatible with route.py / vision_prompt.md."""
        street_map = {
            "preflop": "preflop", "flop": "flop",
            "turn": "turn", "river": "river",
        }
        to_call = self._compute_to_call() if self.game_phase == "active" else 0

        return {
            "hand": [],
            "held_card": self.held_card,
            "robot_state": self.robot_state,
            "community_cards": list(self.community_cards),
            "street": street_map.get(self.street, "preflop"),
            "my_chips": self.robot.chips.to_list(),
            "players": [{
                "seat": "BTN" if self.dealer == "opponent" else "BB",
                "chips": self.opponent.chips.to_list(),
                "status": "folded" if self.opponent.folded else "active",
                "current_bet": self.opponent.current_bet.to_list(),
            }],
            "pot_chips": self.pot.to_list(),
            "my_current_bet": self.robot.current_bet.to_list(),
            "to_call": to_call,
            "my_position": "BTN" if self.dealer == "robot" else "BB",
            "blinds": {"small": SMALL_BLIND, "big": BIG_BLIND},
            "vision_confidence": 0.95,
            "uncertain_fields": [],
            "is_my_turn": self.is_robot_turn and self.game_phase == "active",
            "game_phase": self.game_phase,
            "action_prompt": (
                self._valid_actions()
                if self.is_robot_turn and self.game_phase == "active"
                else []
            ),
            "scene_stable": True,
        }

    def _to_scene(self):
        """Build scene dict for rendering."""
        return {
            "community_cards": list(self.community_cards),
            "robot_cards": ["??", "??"],
            "robot_state": self.robot_state,
            "held_card": self.held_card,
            "my_chips": self.robot.chips.to_list(),
            "pot_chips": self.pot.to_list(),
            "opponent_chips": self.opponent.chips.to_list(),
            "opponent_bet": self.opponent.current_bet.to_list(),
            "my_bet": self.robot.current_bet.to_list(),
            "my_position": "BTN" if self.dealer == "robot" else "BB",
            "dealer_seat": "BTN" if self.dealer == "robot" else "OPP",
            "is_my_turn": self.is_robot_turn and self.game_phase == "active",
            "game_phase": self.game_phase,
            "to_call": self._compute_to_call() if self.game_phase == "active" else 0,
        }

    def render(self, output_path):
        """Render current game state to an image."""
        return render_scene(self._to_scene(), output_path)

    def summary(self):
        """Print a human-readable game summary."""
        lines = [
            f"Hand #{self.hand_number}  |  Street: {self.street}  |  "
            f"Phase: {self.game_phase}  |  Dealer: {self.dealer}",
            f"Community: {' '.join(self.community_cards) or '(none)'}",
            f"Robot cards: {' '.join(self.robot.hole_cards)}  |  "
            f"Hand cache: L={self.hand_cache['left']} R={self.hand_cache['right']}",
            f"Robot chips: {self.robot.chips}  |  Bet: {self.robot.current_bet}",
            f"Opponent chips: {self.opponent.chips}  |  Bet: {self.opponent.current_bet}",
            f"Pot: {self.pot}",
        ]
        if self.game_phase == "active":
            lines.append(
                f"To call: {self._compute_to_call()}  |  "
                f"Robot's turn: {self.is_robot_turn}  |  "
                f"Actions: {self._valid_actions()}"
            )
        return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────

def cmd_render(sim, args):
    path = args.path
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    sim.render(path)
    print(path)


def cmd_apply(sim, args):
    action_obj = json.loads(args.action_json)
    result = sim.apply_action(action_obj)
    print(json.dumps(result))


def cmd_state(sim, args):
    print(json.dumps(sim.get_game_state(), indent=2))


def cmd_interactive(sim, args):
    sim.new_hand()
    print("=== Poker Simulator (interactive) ===")
    print(f"Starting chips per player: {STARTING_COUNT}×{DENOMS}")
    print(f"Blinds: {SMALL_BLIND}/{BIG_BLIND}\n")

    while sim.game_phase != "game_over":
        print(f"\n{'='*60}")
        print(sim.summary())
        print(f"{'='*60}")

        if sim.game_phase == "between_hands" or sim.game_phase == "showdown":
            # show last log entry if showdown
            for entry in sim.action_log:
                if isinstance(entry, dict) and entry.get("event") == "showdown":
                    print(f"\nShowdown: Robot={entry['robot_hand']}, "
                          f"Opponent={entry['opponent_hand']}, "
                          f"Winner={entry['winner']}")
            input("\nPress Enter for next hand...")
            sim.new_hand()
            continue

        if not sim.is_robot_turn or sim.game_phase != "active":
            print("Waiting... (not robot's turn)")
            continue

        print("\nActions: " + ", ".join(sim._valid_actions()))
        print("  view_card left|right / put_down_card / fold / check / call / raise <N> / all_in")

        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0]

        if cmd == "view_card":
            pos = parts[1] if len(parts) > 1 else "left"
            sim.apply_action({"action": "view_card", "position": pos})
        elif cmd == "put_down_card":
            sim.apply_action({"action": "put_down_card"})
        elif cmd == "fold":
            sim.apply_action({"action": "fold"})
        elif cmd == "check":
            sim.apply_action({"action": "check"})
        elif cmd == "call":
            to_call = sim._compute_to_call()
            sim.apply_action({"action": "call", "bet_chips": to_call})
        elif cmd == "raise":
            amount = int(parts[1]) if len(parts) > 1 else BIG_BLIND * 2
            sim.apply_action({"action": "raise", "bet_chips": amount})
        elif cmd == "all_in":
            sim.apply_action({"action": "all_in"})
        elif cmd in ("quit", "exit", "q"):
            break
        else:
            print(f"Unknown command: {cmd}")

    print("\nGame over!")
    print(f"Robot chips: {sim.robot.chips.total()}")
    print(f"Opponent chips: {sim.opponent.chips.total()}")


def cmd_auto(sim, args):
    """Auto-play: random robot vs opponent AI."""
    rounds = args.rounds
    render_dir = args.render_dir

    if render_dir:
        os.makedirs(render_dir, exist_ok=True)

    sim.new_hand()
    hand = 0

    while sim.game_phase != "game_over" and hand < rounds:
        if sim.game_phase in ("between_hands", "showdown"):
            for entry in sim.action_log:
                if isinstance(entry, dict) and entry.get("event") == "showdown":
                    print(f"  Showdown: Robot={entry['robot_hand']}, "
                          f"Opp={entry['opponent_hand']}, "
                          f"Winner={entry['winner']}")
            print(f"  Robot={sim.robot.chips.total()}, "
                  f"Opp={sim.opponent.chips.total()}")
            sim.new_hand()
            hand += 1
            if sim.game_phase == "game_over":
                break
            print(f"\n--- Hand {sim.hand_number} ---")
            continue

        if not sim.is_robot_turn or sim.game_phase != "active":
            continue

        if render_dir:
            sim.render(os.path.join(render_dir, f"h{sim.hand_number:03d}_{sim.street}.jpg"))

        # random robot strategy
        to_call = sim._compute_to_call()
        if to_call > 0:
            r = random.random()
            if r < 0.15:
                action = {"action": "fold"}
            elif r < 0.75:
                action = {"action": "call", "bet_chips": to_call}
            else:
                raise_to = to_call * 2 + sim.robot.street_invested
                action = {"action": "raise", "bet_chips": raise_to}
        else:
            r = random.random()
            if r < 0.65:
                action = {"action": "check"}
            else:
                action = {"action": "raise", "bet_chips": BIG_BLIND * 2}

        print(f"  Robot: {action}")
        sim.apply_action(action)

    print(f"\nDone after {hand} hands.")
    print(f"Robot: {sim.robot.chips.total()}, Opponent: {sim.opponent.chips.total()}")


def main():
    parser = argparse.ArgumentParser(
        description="Poker game simulator for dexholdem loop testing.",
    )
    sub = parser.add_subparsers(dest="command")

    # interactive (default)
    sub.add_parser("interactive", help="Interactive play mode")

    # render
    p_render = sub.add_parser("render", help="Render current state to image")
    p_render.add_argument("path", help="Output image path")

    # apply
    p_apply = sub.add_parser("apply", help="Apply an action")
    p_apply.add_argument("action_json", help="Action JSON string")

    # state
    sub.add_parser("state", help="Print game state JSON")

    # auto
    p_auto = sub.add_parser("auto", help="Auto-play with random robot")
    p_auto.add_argument("--rounds", type=int, default=20,
                        help="Max hands to play (default: 20)")
    p_auto.add_argument("--render-dir", default=None,
                        help="Save rendered images to this directory")

    args = parser.parse_args()

    sim = PokerSimulator()
    sim.new_hand()

    if args.command == "render":
        cmd_render(sim, args)
    elif args.command == "apply":
        cmd_apply(sim, args)
    elif args.command == "state":
        cmd_state(sim, args)
    elif args.command == "auto":
        cmd_auto(sim, args)
    else:
        cmd_interactive(sim, args)


if __name__ == "__main__":
    main()
