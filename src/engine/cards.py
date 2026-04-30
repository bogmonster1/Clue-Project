import random

class Card:
    def __init__(self, name, card_type):
        self.name = name
        self.card_type = card_type


class Deck:
    def __init__(self, data):
        # We read the dictionary keys ("persons", "weapons", "rooms")
        # and create a Card object for every name in those lists.
        self.person_cards = [Card(name, "Person") for name in data["persons"]]
        self.weapon_cards = [Card(name, "Weapon") for name in data["weapons"]]
        self.room_cards = [Card(name, "Room") for name in data["rooms"]]

    def create_murder_envelope(self):
        random.shuffle(self.person_cards)
        random.shuffle(self.weapon_cards)
        random.shuffle(self.room_cards)

        return [self.person_cards.pop(), self.weapon_cards.pop(), self.room_cards.pop()]

    def create_dealable_deck(self):
        dealable_deck = self.person_cards + self.weapon_cards + self.room_cards
        random.shuffle(dealable_deck)
        return dealable_deck
