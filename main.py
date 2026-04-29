import tkinter as tk
import os
from src.utils.data_loader import DataLoader
from src.engine.cards import Deck
from src.engine.board import Board
from src.engine.player_state import Player
from src.engine.game_manager import GameManager
from src.utils.gui import GUI


def main():
    print("--- Booting Watson Games Clue! Simulation ---")

    # 1. Start the Data Pipeline
    # Pass the actual relative paths to where the JSON files will live
    loader = DataLoader(
        items_filepath="data/game_items.json",
        board_filepath="data/board_layout.json"
    )

    if os.path.exists("data/game_items.json"):
        print("Loading external JSON data...")
        game_items_dict = loader.load_game_items()
        board_layout_dict = loader.load_board_layout()
    else:
        print("JSON files not found. Falling back to prototype data...")
        game_items_dict = loader.get_prototype_data()
        board_layout_dict = {}  # Empty dict for prototype grid

    # 2. Initialize Core Components
    deck = Deck(game_items_dict)

    # Pass the grid data and the list of room names to the Board
    board = Board(grid_data=board_layout_dict, room_data=game_items_dict["rooms"])

    # 3. Create Players
    p1 = Player("Miss Scarlett")
    p2 = Player("Col Mustard")
    p3 = Player("Mrs White")
    players = [p1, p2, p3]

    # 4. Start the Engine
    engine = GameManager(players, deck, board)
    engine.setup()

    print("Backend Engine Ready. Launching GUI...")

    # 5. Start the GUI
    root = tk.Tk()
    root.title("Watson Games - Clue! Simulation")

    # Set a default window size (e.g., 900x900)
    root.geometry("900x900")

    # Instantiate the GUI class, passing it the root window and your engine
    app = GUI(root, engine)

    # Start the tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()