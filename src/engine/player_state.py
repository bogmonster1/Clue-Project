import random


class Player:

    def __init__(self, name):
        self.token = None
        self.held_cards = []
        self.location = None
        self.falsely_accused = False
        self.name = name

    def give_card(self, card):
        self.held_cards.append(card)

    def get_matches(self, person, weapon, room):
        matches = []
        for card in self.held_cards:
            if card.name in [person, weapon, room]:
                matches.append(card)
        return matches

    def choose_card(self, matches):
        return random.choice(matches)
