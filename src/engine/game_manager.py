import random

from src.engine.board import Board
from src.engine.movement import MovementCheck


class GameManager:
    def __init__(self, players, deck, board):
        self.movement_validator = MovementCheck(board)
        self.players = players
        self.deck = deck
        self.board = board
        self.murder_envelope = []
        self.current_player_index = 0
        self.game_over = False

    def setup(self):
        """Sets up the initial game state."""
        self.murder_envelope = self.deck.create_murder_envelope()
        print(self.murder_envelope[0].name, self.murder_envelope[1].name, self.murder_envelope[2].name)
        dealable_deck = self.deck.create_dealable_deck()
        self.deal_cards(dealable_deck)

        self.board.setup_initial_locations(self.players)

        # Tradition dictates Miss Scarlett goes first.
        for i in range(len(self.players)):
            if self.players[i].name == "Miss Scarlett":
                self.current_player_index = i
                return
        self.current_player_index = 0

    def deal_cards(self, dealable_deck):
        receive_index = 0
        player_count = len(self.players)

        while len(dealable_deck) != 0:
            card = dealable_deck.pop()
            self.players[receive_index].give_card(card)
            receive_index = (receive_index + 1) % player_count

    # ==========================================
    # TURN API (Called by the GUI)
    # ==========================================

    def get_current_player(self):
        """Helper for the GUI to know whose turn it is."""
        return self.players[self.current_player_index]

    def handle_roll(self):
        """
        GUI calls this when user clicks [Roll Dice].
        Returns the roll number and a list of valid destination coordinates.
        """
        player = self.get_current_player()
        roll = random.randint(1, 6)

        valid_moves = self.movement_validator.get_valid_moves(player.location, roll)
        return roll, valid_moves

    def handle_move(self, destination):
        """
        GUI calls this after the user selects a valid move square.
        """
        player = self.get_current_player()

        # If the GUI accidentally sends a string like "(7, 22)", this fixes it instantly.
        if isinstance(destination, str) and destination.startswith("("):
            destination = eval(destination)

        self.board.move_piece(player.name, destination)
        player.location = destination

    def get_available_passage(self):
        """
        GUI calls this at the start of a turn.
        Returns the destination room string if a passage exists, otherwise None.
        """
        player = self.get_current_player()
        if self.board.is_room(player.location):
            return self.movement_validator.check_passage(player.location)
        return None

    def handle_passage(self):
        """
        GUI calls this if the user clicks [Take Secret Passage] instead of [Roll Dice].
        """
        player = self.get_current_player()
        destination = self.movement_validator.check_passage(player.location)

        if destination:
            self.board.move_piece(player.name, destination)
            player.location = destination
            return destination

    def handle_suggestion(self, suggested_person, suggested_weapon):
        """
        GUI calls this when user submits a suggestion in a room.
        Returns the Card object that disproves it, or None if no one can.
        """
        current_player = self.get_current_player()
        room = current_player.location  # Suggestion must be current room

        # Teleport the suggested items to the room
        self.board.move_piece(suggested_person, room)
        self.board.move_weapon(suggested_weapon, room)

        # Update the actual player object so the GUI token moves
        for p in self.players:
            if p.name == suggested_person:
                p.location = room
                break

        # Go around the table to disprove it
        num_players = len(self.players)
        for step in range(1, num_players):
            check_index = (self.current_player_index + step) % num_players
            check_player = self.players[check_index]

            matches = check_player.get_matches(suggested_person, suggested_weapon, room)
            if matches:
                # Returns the first matched card for now
                return check_player.choose_card(matches)

        return None  # No one could disprove it

    def handle_accusation(self, accused_person, accused_weapon, accused_room):
        """
        GUI calls this when user submits a final accusation.
        Returns True if they won, False if they lost.
        """
        current_player = self.get_current_player()
        envelope_names = [card.name for card in self.murder_envelope]

        if accused_person in envelope_names and accused_weapon in envelope_names and accused_room in envelope_names:
            self.game_over = True
            return True
        else:
            current_player.falsely_accused = True
            return False

    def end_turn(self):
        """
        GUI calls this when the player's turn is completely over.
        Advances the index to the next active player.
        """

        # Check if everyone lost
        if all(p.falsely_accused for p in self.players):
            self.game_over = True
            return

        # Move clockwise to the next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # Skip players who falsely accused
        while self.get_current_player().falsely_accused:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
