class GameManager:
    def __init__(self, players, deck, board):
        """
        :param players: list of players
        :param deck:
        :param board:
        """

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

    def find_dealer(self):
        pass

    def roll_dice(self):
        pass

    def play_turn(self, player):
        pass

    def suggestion(self, current_player, suggested_person, suggested_weapon, room):
        pass

    def accusation(self, current_player, accused_person, accused_weapon, accused_room):
        pass
