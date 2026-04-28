import random
from movement import MovementCheck

class GameManager:
    def __init__(self, players, deck, board):
        """
        :param players: list of players
        :param deck:
        :param board:
        """

        self.movement_validator = MovementCheck(board)
        self.players = players
        self.deck = deck
        self.board = board
        self.murder_envelope = []
        self.current_player_index = 0
        self.game_over = False

    def setup(self):
        self.murder_envelope = self.deck.create_murder_envelope()
        dealable_deck = self.deck.create_dealable_deck()
        self.deal_cards(dealable_deck)

    def deal_cards(self, dealable_deck):
        dealer_index = self.find_dealer()
        receive_index = dealer_index
        player_count = len(self.players)

        while len(dealable_deck) != 0:
            card = dealable_deck.pop()
            self.players[receive_index].give_card(card)
            receive_index = (receive_index + 1) % player_count

    def roll_dice(self):
        return random.randint(1, 6)

    def run_game(self):
        """The main loop that keeps the game running until someone wins."""
        print("\n=== STARTING GAME ===")

        # Tradition dictates Miss Scarlett goes first.
        # TODO Add check to see who if anyone is Miss scarlett. if no one, just set to first player
        self.current_player_index = 0

        while not self.game_over:
            current_player = self.players[self.current_player_index]

            # If the player made a wrong accusation, they lose their turns.
            if current_player.falsely_accused:
                # TODO display to gui that they skipped go
                pass
            else:
                self.play_turn(current_player)

            if self.game_over:
                break

            # Move clockwise to the next player
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def play_turn(self, player):
        """Executes the logic flow of a single turn."""

        # 1. MOVEMENT PHASE
        # Secret passages can be used instead of rolling the dice
        passage_dest = None
        if self.board.is_room(player.location):
            passage_dest = self.movement_validator.check_passage(player.location)

        use_passage = False
        if passage_dest:
            # TODO ask if they want to use the passage or roll
            if use_passage:
                self.board.move_piece(player.token, passage_dest)
                player.location = passage_dest

        # If they didn't use a passage, they must roll
        if not passage_dest or not use_passage:
            roll = self.roll_dice()

            # Get valid destinations
            valid_moves = self.movement_validator.get_valid_moves(player.location, roll)

            # TODO display valid_moves and await a choice
            # chosen_move = ...
            # self.board.move_piece(player.token, chosen_move)
            # player.location = chosen_move

        # 2. SUGGESTION PHASE
        # A player may make a suggestion only when their playing piece is in the room [cite: 97]
        if self.board.is_room(player.location):
            # TODO ask if they want to make a suggestion, and get the inputs
            wants_to_suggest = True
            if wants_to_suggest:
                print(f"(TODO: Player inputs suggestion for {player.location})")
                # self.suggestion(player, chosen_person, chosen_weapon, player.location)

        # 3. ACCUSATION PHASE
        # TODO ask if they want to make their final accusation
        wants_to_accuse = False
        if wants_to_accuse:
            pass
            # TODO give options of accusations
            # self.accusation(player, acc_person, acc_weapon, acc_room)

    def suggestion(self, current_player, suggested_person, suggested_weapon, room):
        self.board.move_piece(suggested_person, room)
        self.board.move_weapon(suggested_weapon, room)

        current_index = self.players.index(current_player)
        num_players = len(self.players)

        for step in range(1, num_players):
            check_index = (current_index + step) % num_players
            check_player = self.players[check_index]

            matches = check_player.get_matches(suggested_person, suggested_weapon, room)
            if matches:
                revealed_card = check_player.choose_card(matches)
                return revealed_card
        return None

    def accusation(self, current_player, accused_person, accused_weapon, accused_room):
        envelope_names = [card.name for card in self.murder_envelope]

        if accused_person in envelope_names and accused_weapon in envelope_names and accused_room in envelope_names:
            self.game_over = True
            return True
        else:
            current_player.falsely_accused = True
            return False
