import json

class DataLoader:
    def __init__(self, items_filepath, board_filepath):
        self.items_filepath = items_filepath
        self.board_filepath = board_filepath

    def load_game_items(self):
        """Reads the items JSON and returns a Python dictionary."""
        with open(self.items_filepath, 'r') as file:
            return json.load(file)

    def load_board_layout(self):
        """Reads the board grid JSON and returns a Python dictionary."""
        with open(self.board_filepath, 'r') as file:
            return json.load(file)

    def get_prototype_data(self):
        """Returns hardcoded data so the prototype can compile today."""
        return {
            "persons": ["Miss Scarlett", "Col Mustard", "Mrs White", "Rev Green", "Mrs Peacock", "Prof Plum"],
            "weapons": ["Dagger", "Candlestick", "Revolver", "Rope", "Lead Piping", "Spanner"],
            "rooms": ["Hall", "Lounge", "Dining Room", "Kitchen", "Ball Room", "Conservatory", "Billiard Room",
                      "Library", "Study"]
        }