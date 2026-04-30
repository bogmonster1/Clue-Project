class MovementCheck:
    def __init__(self, board):
        self.board = board
        # Dynamically load from JSON instead of hardcoding
        self.secret_passages = self.board.grid.get("secret_passages", {})

    def check_passage(self, current_room):
        """
        Checks if the current room has a secret passage.
        Returns the destination room string, or None if no passage exists.
        """
        # Secret passages enable players to move from certain rooms to those indicated on the board.
        return self.secret_passages.get(current_room)

    def get_valid_moves(self, start_loc, dice_roll):
        """
        Calculates exact-distance moves using Path-Tracking.
        Prevents doubling back, but finds all valid exact-length routes.
        """
        if start_loc is None:
            return []

        starting_coords = []
        if isinstance(start_loc, str):
            # If in a room, find all doors for this room to exit from
            doors = self.board.grid.get("doors", [])
            for door in doors:
                if door["room"] == start_loc:
                    starting_coords.append(tuple(door["grid_coord"]))
            if not starting_coords:
                return []  # Trapped! (No doors defined)
        else:
            # Standard coordinate start
            starting_coords.append(start_loc)

        valid_destinations = set()

        # Cache the door coordinates for fast lookup
        door_coords = {tuple(d["grid_coord"]) for d in self.board.grid.get("doors", [])}

        for start_coord in starting_coords:
            queue = [(start_coord, [start_coord])]

            while queue:
                current_coord, path = queue.pop(0)

                # If we hit a door (and didn't start exactly on it), we can stop early!
                if current_coord in door_coords and current_coord != start_coord:
                    valid_destinations.add(current_coord)
                    continue  # Entering a room ends the move count

                # Existing exact-distance check
                if len(path) - 1 == dice_roll:
                    valid_destinations.add(current_coord)
                    continue

                for neighbor in self.board.get_adjacent_squares(current_coord):
                    if self.board.is_wall(current_coord, neighbor):
                        continue
                    if self.board.is_square_occupied(neighbor) and neighbor != start_coord:
                        continue

                    if neighbor not in path:
                        new_path = list(path)
                        new_path.append(neighbor)
                        queue.append((neighbor, new_path))

        return list(valid_destinations)
