"""
agent.py  —  Autonomous game player agent for Watson Games Clue!
----------------------------------------------------------------
Strategy:
  - Tracks all cards it has seen (held or revealed by others).
  - Prefers to suggest unknowns to gain information.
  - Only accuses when exactly one unknown remains in each category.
  - Movement biases toward rooms (where suggestions can be made).
  - Uses secret passages randomly (50% chance).
"""

import random


class AgentPlayer:
    """Autonomous player agent wrapping a Player instance."""

    def __init__(self, player, game_items):
        self.player = player
        self.is_agent = True

        # Cards the agent knows are NOT in the murder envelope
        self.unknown_persons = list(game_items["persons"])
        self.unknown_weapons = list(game_items["weapons"])
        self.unknown_rooms = list(game_items["rooms"])

        # Immediately eliminate cards in our own hand
        for card in self.player.held_cards:
            self._mark_known(card.name)

    def _mark_known(self, card_name):
        """Remove a card from all unknown lists."""
        for lst in (self.unknown_persons, self.unknown_weapons, self.unknown_rooms):
            if card_name in lst:
                lst.remove(card_name)

    def receive_disproof(self, card):
        """Called when another player shows this agent a disproof card."""
        if card:
            self._mark_known(card.name)

    # ------------------------------------------------------------------
    # Decision helpers
    # ------------------------------------------------------------------

    def decide_move(self, valid_moves, board):
        """Prefer room destinations; fall back to random."""
        if not valid_moves:
            return None
        room_moves = [m for m in valid_moves if board.is_room(m)]
        return random.choice(room_moves if room_moves else valid_moves)

    def decide_suggestion(self):
        """Suggest unknowns to gain info; random fallback."""
        persons = self.unknown_persons or [c.name for c in self.player.held_cards
                                           if c.card_type == "Person"] or ["Miss Scarlett"]
        weapons = self.unknown_weapons or [c.name for c in self.player.held_cards
                                           if c.card_type == "Weapon"] or ["Dagger"]
        return random.choice(persons), random.choice(weapons)

    def decide_accusation(self):
        """Only accuse when fully confident (1 unknown in each category)."""
        if (len(self.unknown_persons) == 1 and
                len(self.unknown_weapons) == 1 and
                len(self.unknown_rooms) == 1):
            return (self.unknown_persons[0],
                    self.unknown_weapons[0],
                    self.unknown_rooms[0])
        return None

    def use_secret_passage(self, passage_dest):
        return bool(passage_dest) and random.random() < 0.5

    # ------------------------------------------------------------------
    # Full turn
    # ------------------------------------------------------------------

    def execute_turn(self, engine):
        """
        Drive a complete autonomous turn via the GameManager API.
        Returns a log dict for the GUI to display.
        """
        log = {"player": self.player.name, "actions": []}

        if engine.game_over:
            return log

        # 1. Secret passage?
        passage_dest = engine.get_available_passage()
        if self.use_secret_passage(passage_dest):
            dest = engine.handle_passage()
            log["actions"].append(f"Used secret passage to {dest}")
        else:
            # 2. Roll & move
            roll, valid_moves = engine.handle_roll()
            log["actions"].append(f"Rolled {roll}")
            if valid_moves:
                chosen = self.decide_move(valid_moves, engine.board)
                engine.handle_move(chosen)
                log["actions"].append(f"Moved to {chosen}")
            else:
                log["actions"].append("No valid moves — stayed put")

        # 3. Suggest if in a room
        if engine.board.is_room(self.player.location):
            person, weapon = self.decide_suggestion()
            result_card = engine.handle_suggestion(person, weapon)
            log["actions"].append(
                f"Suggested {person} w/ {weapon} in {self.player.location}"
            )
            if result_card:
                self.receive_disproof(result_card)
                log["actions"].append(f"Suggestion was disproved (card kept secret)")
            else:
                log["actions"].append("No one could disprove it")

            # 4. Accuse if certain
            accusation = self.decide_accusation()
            if accusation:
                p, w, r = accusation
                won = engine.handle_accusation(p, w, r)
                log["won"] = won
                log["actions"].append(
                    f"Accused {p} / {w} / {r} — {'WIN!' if won else 'Wrong!'}"
                )

        # 5. End turn
        engine.end_turn()
        return log
