class Board:
    def __init__(self, grid_data, room_data):
        self.grid = grid_data
        self.room = room_data
        self.piece_locations = {}
        self.weapon_locations = {}

    def setup_initial_locations(self):
        pass

    def move_piece(self, piece, room):
        self.piece_locations[piece] = room

    def move_weapon(self, weapon, room):
        self.weapon_locations[weapon] = room

    def is_wall(self, current_coord, next_coord):
        """
        TODO check the grid data to see if a solid wall exists directly between current_coord and next_coord.
        Returns True if blocked, False if clear.
        """
        pass

    def get_adjacent_squares(self, coord):
        """
        TODO return a list of (x,y) tuples that are strictly Up, Down, Left, or Right of the given coord.
        """
        pass

    def is_square_occupied(self, coord):
        """Checks if another player is currently on this square."""
        for location in self.piece_locations.values():
            if location == coord:
                return True
        return False

    def is_doorway(self, current_coord, next_coord):
        """
        TODO check if moving between these two coords constitutes entering a room through a door.
        """
        pass

    def is_room(self, location):
        """Checks if the current location is a Room name rather than a coordinate."""
        return location in self.room