import random

class Card:
    def __init__(self, name, card_type):
        self.name = name
        self.card_type = card_type


class Deck:
    def __init__(self, data):
        self.person_cards = []
        self.weapon_cards = []
        self.room_cards = []
        # made using the passed in data i.e. = [Card(name, "person") for person in (data: where person)]

    def create_murder_envelope(self):
        random.shuffle(self.person_cards)
        random.shuffle(self.weapon_cards)
        random.shuffle(self.room_cards)

        return [self.person_cards.pop(), self.weapon_cards.pop(), self.room_cards.pop()]

    def create_dealable_deck(self):
        dealable_deck = self.person_cards + self.weapon_cards + self.room_cards
        random.shuffle(dealable_deck)
        return dealable_deck
