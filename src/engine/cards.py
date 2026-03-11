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
        pass

    def create_dealable_deck(self):
        pass
