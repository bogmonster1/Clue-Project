class Player:

    def __init__(self):
        self.token = None
        self.held_cards = []
        self.location = None
        self.falsely_accused = False

    def give_card(self, card):
        self.held_cards.append(card)