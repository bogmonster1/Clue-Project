"""
test_clue.py  —  Unit tests for Watson Games Clue! simulation
-------------------------------------------------------------
Run with:  python -m pytest test_clue.py -v
           (or)  python test_clue.py
"""

import sys
import os
import unittest
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.engine.board import Board
from src.engine.cards import Card, Deck
from src.engine.player_state import Player
from src.engine.game_manager import GameManager
from src.engine.movement import MovementCheck
from src.engine.agent import AgentPlayer

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

GAME_ITEMS = {
    "persons": ["Miss Scarlett", "Col Mustard", "Mrs White",
                "Rev Green", "Mrs Peacock", "Prof Plum"],
    "weapons": ["Dagger", "Candlestick", "Revolver",
                "Rope", "Lead Piping", "Spanner"],
    "rooms": ["Hall", "Lounge", "Dining Room", "Kitchen", "Ball Room",
              "Conservatory", "Billiard Room", "Library", "Study"]
}


def make_engine(num_players=3):
    players = [Player(n) for n in GAME_ITEMS["persons"][:num_players]]
    deck = Deck(GAME_ITEMS)
    board = Board(grid_data={}, room_data=GAME_ITEMS["rooms"])
    engine = GameManager(players, deck, board)
    engine.setup()
    return engine, players, board


# ---------------------------------------------------------------------------
# Card tests
# ---------------------------------------------------------------------------

class TestCards(unittest.TestCase):

    def test_murder_envelope_has_three_cards(self):
        deck = Deck(GAME_ITEMS)
        envelope = deck.create_murder_envelope()
        self.assertEqual(len(envelope), 3)

    def test_murder_envelope_has_one_of_each_type(self):
        deck = Deck(GAME_ITEMS)
        envelope = deck.create_murder_envelope()
        types = {c.card_type for c in envelope}
        self.assertEqual(types, {"Person", "Weapon", "Room"})

    def test_dealable_deck_missing_envelope_cards(self):
        deck = Deck(GAME_ITEMS)
        envelope = deck.create_murder_envelope()
        dealable = deck.create_dealable_deck()
        envelope_names = {c.name for c in envelope}
        dealable_names = {c.name for c in dealable}
        # None of the envelope cards should appear in the dealable deck
        self.assertTrue(envelope_names.isdisjoint(dealable_names))

    def test_total_cards_add_up(self):
        # 6 persons + 6 weapons + 9 rooms = 21 total; 3 in envelope, 18 dealt
        deck = Deck(GAME_ITEMS)
        envelope = deck.create_murder_envelope()
        dealable = deck.create_dealable_deck()
        self.assertEqual(len(envelope) + len(dealable), 21)


# ---------------------------------------------------------------------------
# Board / movement tests
# ---------------------------------------------------------------------------

class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board(grid_data={}, room_data=GAME_ITEMS["rooms"])

    def test_is_room_recognises_rooms(self):
        for room in GAME_ITEMS["rooms"]:
            self.assertTrue(self.board.is_room(room))

    def test_is_room_rejects_coordinates(self):
        self.assertFalse(self.board.is_room((5, 5)))
        self.assertFalse(self.board.is_room(None))

    def test_adjacent_squares_centre(self):
        neighbours = self.board.get_adjacent_squares((5, 5))
        self.assertIn((5, 4), neighbours)  # Up
        self.assertIn((5, 6), neighbours)  # Down
        self.assertIn((4, 5), neighbours)  # Left
        self.assertIn((6, 5), neighbours)  # Right

    def test_adjacent_squares_corner_clamps(self):
        # Top-left corner: no up or left
        neighbours = self.board.get_adjacent_squares((0, 0))
        self.assertNotIn((-1, 0), neighbours)
        self.assertNotIn((0, -1), neighbours)
        self.assertEqual(len(neighbours), 2)

    def test_occupied_square_detection(self):
        self.board.piece_locations["P1"] = (3, 3)
        self.assertTrue(self.board.is_square_occupied((3, 3)))
        self.assertFalse(self.board.is_square_occupied((3, 4)))

    def test_move_piece_updates_location(self):
        self.board.move_piece("Miss Scarlett", "Lounge")
        self.assertEqual(self.board.piece_locations["Miss Scarlett"], "Lounge")


class TestMovement(unittest.TestCase):

    def setUp(self):
        self.board = Board(grid_data={}, room_data=GAME_ITEMS["rooms"])
        self.mover = MovementCheck(self.board)

    def test_roll_1_gives_adjacent_squares(self):
        moves = self.mover.get_valid_moves((5, 5), 1)
        # With no walls or occupants, there are 4 adjacent squares
        self.assertEqual(len(moves), 4)
        self.assertIn((5, 4), moves)
        self.assertIn((5, 6), moves)

    def test_no_moves_from_none(self):
        moves = self.mover.get_valid_moves(None, 3)
        self.assertEqual(moves, [])

    def test_secret_passage_lounge_to_conservatory(self):
        dest = self.mover.check_passage("Lounge")
        self.assertEqual(dest, "Conservatory")

    def test_secret_passage_none_for_non_corner(self):
        self.assertIsNone(self.mover.check_passage("Hall"))
        self.assertIsNone(self.mover.check_passage("Library"))

    def test_roll_cannot_exceed_grid_boundary(self):
        # Start at top-left corner; roll 2
        moves = self.mover.get_valid_moves((0, 0), 2)
        for m in moves:
            col, row = m
            self.assertGreaterEqual(col, 0)
            self.assertGreaterEqual(row, 0)


# ---------------------------------------------------------------------------
# Player state tests
# ---------------------------------------------------------------------------

class TestPlayer(unittest.TestCase):

    def test_give_card(self):
        p = Player("Miss Scarlett")
        card = Card("Dagger", "Weapon")
        p.give_card(card)
        self.assertIn(card, p.held_cards)

    def test_get_matches_finds_held_cards(self):
        p = Player("Col Mustard")
        p.give_card(Card("Dagger", "Weapon"))
        p.give_card(Card("Hall", "Room"))
        matches = p.get_matches("Miss Scarlett", "Dagger", "Lounge")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "Dagger")

    def test_get_matches_empty_when_no_overlap(self):
        p = Player("Mrs White")
        p.give_card(Card("Revolver", "Weapon"))
        matches = p.get_matches("Col Mustard", "Dagger", "Hall")
        self.assertEqual(matches, [])


# ---------------------------------------------------------------------------
# Game manager tests
# ---------------------------------------------------------------------------

class TestGameManager(unittest.TestCase):

    def setUp(self):
        self.engine, self.players, self.board = make_engine(num_players=3)

    def test_setup_assigns_all_cards(self):
        # Every non-envelope card must be held by someone
        all_held = []
        for p in self.players:
            all_held.extend(c.name for c in p.held_cards)
        # 21 total cards - 3 in envelope = 18 dealt
        self.assertEqual(len(all_held), 18)

    def test_miss_scarlett_goes_first(self):
        self.assertEqual(self.engine.get_current_player().name, "Miss Scarlett")

    def test_handle_roll_returns_valid_data(self):
        roll, moves = self.engine.handle_roll()
        self.assertIn(roll, range(1, 7))
        self.assertIsInstance(moves, list)

    def test_handle_move_updates_player_location(self):
        player = self.engine.get_current_player()
        _, moves = self.engine.handle_roll()
        if moves:
            dest = moves[0]
            self.engine.handle_move(dest)
            self.assertEqual(player.location, dest)

    def test_end_turn_advances_player(self):
        first = self.engine.get_current_player().name
        self.engine.end_turn()
        second = self.engine.get_current_player().name
        self.assertNotEqual(first, second)

    def test_correct_accusation_wins(self):
        envelope_names = [c.name for c in self.engine.murder_envelope]
        won = self.engine.handle_accusation(*envelope_names)
        self.assertTrue(won)
        self.assertTrue(self.engine.game_over)

    def test_wrong_accusation_does_not_win(self):
        # Deliberately wrong accusation
        won = self.engine.handle_accusation("Miss Scarlett", "Dagger", "Hall")
        # This could theoretically be correct; re-try with impossible combo
        # by using envelope contents + 1 wrong card
        envelope = [c.name for c in self.engine.murder_envelope]
        wrong_person = next(n for n in GAME_ITEMS["persons"] if n != envelope[0])
        won = self.engine.handle_accusation(wrong_person, envelope[1], envelope[2])
        self.assertFalse(won)

    def test_falsely_accused_player_is_skipped(self):
        # Force first player (Miss Scarlett) to be falsely accused
        self.players[0].falsely_accused = True
        self.engine.end_turn()
        # Should skip to player 2, not player 1
        self.assertNotEqual(self.engine.get_current_player().name, "Miss Scarlett")

    def test_suggestion_teleports_suspect(self):
        player = self.engine.get_current_player()
        player.location = "Hall"
        self.board.move_piece(player.name, "Hall")
        self.engine.handle_suggestion("Col Mustard", "Dagger")
        # Col Mustard's piece should now be in Hall
        self.assertEqual(self.board.piece_locations.get("Col Mustard"), "Hall")

    def test_dice_is_fair(self):
        """Statistical test: over 600 rolls, each face should appear ~100 times."""
        random.seed(42)
        counts = [0] * 7
        for _ in range(600):
            roll, _ = self.engine.handle_roll()
            counts[roll] += 1
            self.engine.end_turn()  # advance so we can keep rolling
        for face in range(1, 7):
            self.assertGreater(counts[face], 50,
                               f"Face {face} appeared too rarely: {counts[face]}")


# ---------------------------------------------------------------------------
# Agent tests
# ---------------------------------------------------------------------------

class TestAgent(unittest.TestCase):

    def setUp(self):
        self.engine, self.players, self.board = make_engine(num_players=3)
        self.agent = AgentPlayer(self.players[0], GAME_ITEMS)

    def test_agent_knows_own_cards(self):
        for card in self.players[0].held_cards:
            self.assertNotIn(card.name, self.agent.unknown_persons +
                             self.agent.unknown_weapons + self.agent.unknown_rooms)

    def test_receive_disproof_removes_from_unknowns(self):
        # Inject a fake unknown weapon
        self.agent.unknown_weapons = ["Dagger"]
        fake_card = Card("Dagger", "Weapon")
        self.agent.receive_disproof(fake_card)
        self.assertNotIn("Dagger", self.agent.unknown_weapons)

    def test_only_accuses_when_certain(self):
        # Not certain yet
        self.assertIsNone(self.agent.decide_accusation())

        # Make it certain
        self.agent.unknown_persons = ["Miss Scarlett"]
        self.agent.unknown_weapons = ["Dagger"]
        self.agent.unknown_rooms = ["Hall"]
        result = self.agent.decide_accusation()
        self.assertIsNotNone(result)
        self.assertEqual(result, ("Miss Scarlett", "Dagger", "Hall"))

    def test_execute_turn_runs_without_error(self):
        """Smoke test: a full AI turn should not raise."""
        try:
            log = self.agent.execute_turn(self.engine)
            self.assertIn("actions", log)
        except Exception as e:
            self.fail(f"execute_turn raised an exception: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
