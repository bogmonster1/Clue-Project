class Board:
    def __init__(self, grid_data, room_data):
        self.grid = grid_data
        self.room = room_data
        self.piece_locations = {}
        self.weapon_locations = {}

    def setup_initial_locations(self, players):
        """Use the JSON data for starting squares."""
        starting_squares = self.grid.get("starting_squares", {})

        for player in players:
            # Fetch from JSON, convert list [x, y] to tuple (x, y)
            start_pos = starting_squares.get(player.name)
            if start_pos:
                start_pos = tuple(start_pos)
                player.location = start_pos
                self.piece_locations[player.name] = start_pos

    def move_piece(self, piece, room):
        self.piece_locations[piece] = room

    def move_weapon(self, weapon, room):
        self.weapon_locations[weapon] = room

    def is_square_occupied(self, coord):
        """Checks if another player is currently on this square."""
        for location in self.piece_locations.values():
            if location == coord:
                return True
        return False

    def is_room(self, location):
        """Checks if the current location is a Room name rather than a coordinate."""
        return location in self.room

    def get_adjacent_squares(self, coord):
        """
        Returns orthogonal squares, strictly enforcing grid boundaries.
        """
        if isinstance(coord, str) or coord is None:
            return []

        x, y = coord
        neighbors = []

        # Grid boundaries: 24 width (0-23), 25 height (0-24)
        if y > 0:  neighbors.append((x, y - 1))  # Up
        if y < 24: neighbors.append((x, y + 1))  # Down
        if x > 0:  neighbors.append((x - 1, y))  # Left
        if x < 23: neighbors.append((x + 1, y))  # Right

        return neighbors

    def is_doorway(self, current_coord, next_coord):
        """Checks if the destination square is a defined door."""
        doors = self.grid.get("doors", [])
        for door in doors:
            if tuple(door["grid_coord"]) == next_coord:
                return True
        return False

    def is_wall(self, current_coord, next_coord):
        """
        A square is a wall if it falls inside any room's bounding box,
        UNLESS that specific square is a door.
        """
        # 1. If the square they want to step on is a door, it's open!
        if self.is_doorway(current_coord, next_coord):
            return False

        # 2. Otherwise, check if the square is inside any room's borders
        x, y = next_coord
        room_bounds = self.grid.get("room_bounds", [])

        for bounds in room_bounds:
            if bounds["x1"] <= x <= bounds["x2"] and bounds["y1"] <= y <= bounds["y2"]:
                return True  # Hit a solid wall!

        return False
