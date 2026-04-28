class MovementCheck:
    def __init__(self, board):
        self.board = board

        # Secret passages based on the classic Clue! board corners
        self.secret_passages = {
            "Lounge": "Conservatory",
            "Conservatory": "Lounge",
            "Kitchen": "Study",
            "Study": "Kitchen"
        }

    def check_passage(self, current_room):
        """
        Checks if the current room has a secret passage.
        Returns the destination room string, or None if no passage exists.
        """
        # Secret passages enable players to move from certain rooms to those indicated on the board.
        return self.secret_passages.get(current_room)

    def get_valid_moves(self, start_coord, dice_roll):
        """
        Uses Breadth-First Search (BFS) to find all reachable coordinates
        exactly 'dice_roll' steps away, strictly moving orthogonally .
        """
        # Queue stores tuples of (current_coord, remaining_steps)
        queue = [(start_coord, dice_roll)]
        visited = {start_coord}
        valid_destinations = set()

        while queue:
            current_coord, steps_left = queue.pop(0)

            if steps_left == 0:
                valid_destinations.add(current_coord)
                continue

            # Get adjacent squares - No Diagonals
            for neighbor in self.board.get_adjacent_squares(current_coord):
                if self.board.is_wall(current_coord, neighbor):
                    continue

                # Cannot move through another player
                if self.board.is_square_occupied(neighbor):
                    continue

                if neighbor not in visited:
                    visited.add(neighbor)

                    # Check room entry
                    if self.board.is_doorway(current_coord, neighbor):
                        # Entering a room ends the move count immediately
                        valid_destinations.add(neighbor)
                    else:
                        # Normal hallway move, decrement steps and keep searching
                        queue.append((neighbor, steps_left - 1))

        return list(valid_destinations)


