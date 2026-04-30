"""
main.py  —  Entry point for Watson Games Clue! simulation
----------------------------------------------------------
"""

import tkinter as tk
import os

from src.utils.data_loader import DataLoader
from src.engine.cards import Deck
from src.engine.board import Board
from src.engine.player_state import Player
from src.engine.game_manager import GameManager
from src.engine.agent import AgentPlayer
from src.utils.gui import GUI

from pathlib import Path

root_dir = Path(__file__).resolve().parent


def main():
    print("--- Booting Watson Games Clue! Simulation ---")

    # --- 1. Data ---
    loader = DataLoader(
        items_filepath=root_dir/"data/game_items.json",
        board_filepath=root_dir/"data/board_layout.json"
    )
    if os.path.exists("data/game_items.json"):
        print("Loading external JSON data...")
        game_items_dict = loader.load_game_items()
        board_layout_dict = loader.load_board_layout()
    else:
        print("JSON not found — using prototype data.")
        game_items_dict = loader.get_prototype_data()
        board_layout_dict = {}

    # --- 2. Components ---
    deck = Deck(game_items_dict)
    board = Board(grid_data=board_layout_dict,
                  room_data=game_items_dict["rooms"])

    # --- 3. All 6 characters always participate (spare pieces rule) ---
    all_names = ["Miss Scarlett", "Col Mustard", "Mrs White",
                 "Rev Green", "Mrs Peacock", "Prof Plum"]
    players = [Player(name) for name in all_names]

    # --- 4. Pre-Game Setup Window ---
    setup_root = tk.Tk()
    setup_root.title("Game Setup")
    setup_root.geometry("300x350")
    setup_root.configure(bg="#2E3440")

    tk.Label(setup_root, text="Select Human Players:",
             font=("Arial", 12, "bold"), bg="#2E3440", fg="#EBCB8B").pack(pady=15)

    human_vars = {}
    for name in all_names:
        # Default Miss Scarlett to checked, everyone else unchecked
        var = tk.BooleanVar(value=(name == "Miss Scarlett"))
        chk = tk.Checkbutton(setup_root, text=name, variable=var,
                             bg="#2E3440", fg="#ECEFF4", selectcolor="#4C566A",
                             activebackground="#2E3440", activeforeground="white",
                             font=("Arial", 10))
        chk.pack(anchor="w", padx=60, pady=3)
        human_vars[name] = var

    human_names = set()

    def launch_game():
        # Read the checkboxes when the user clicks launch
        for name, var in human_vars.items():
            if var.get():
                human_names.add(name)
        setup_root.destroy()  # Close the setup menu and move on to the game

    tk.Button(setup_root, text="Launch Simulation", command=launch_game,
              bg="#A3BE8C", fg="#2E3440", font=("Arial", 11, "bold"),
              width=20).pack(pady=20)

    # This pauses the script until the user clicks launch or closes the window
    setup_root.mainloop()

    # Calculate AI players based on what the user selected
    ai_names = set(all_names) - human_names

    print(f"Human players : {', '.join(human_names) or 'None'}")
    print(f"AI agents     : {', '.join(ai_names) or 'None'}")

    # --- 5. Engine ---
    engine = GameManager(players, deck, board)
    engine.setup()

    # --- 6. Build agents ---
    agents = {
        player.name: AgentPlayer(player, game_items_dict)
        for player in players
        if player.name in ai_names
    }

    print("Engine ready. Launching GUI...")

    # --- 7. GUI ---
    root = tk.Tk()
    root.title("Watson Games — Clue! Simulation")
    root.geometry("950x660")

    GUI(root, engine, agents=agents)
    root.mainloop()


if __name__ == "__main__":
    main()
