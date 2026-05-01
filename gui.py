"""
gui.py
------
Graphical User Interface for Watson Games Clue! simulation.

Handles:
  - Board canvas with player token rendering
  - Turn-based controls (roll, move, suggest, accuse, end turn)
  - Secret passage button (appears when relevant)
  - Card hand display for the current human player
  - Automated AI agent turns with animated log output
  - Detective notes panel (known-innocent cards)
"""

import tkinter as tk
from tkinter import ttk, messagebox

# Colour tokens per character
PLAYER_COLOURS = {
    "Miss Scarlett": "#e63946",
    "Col Mustard": "#f4a261",
    "Mrs White": "#f1faee",
    "Rev Green": "#2a9d8f",
    "Mrs Peacock": "#457b9d",
    "Prof Plum": "#6a0572",
}

CELL = 25  # pixels per grid square for coordinate->pixel mapping


def coord_to_pixel(coord):
    """Convert a (col, row) grid coordinate to canvas pixel centre."""
    col, row = coord
    return (col * CELL + CELL // 2, row * CELL + CELL // 2)


class GUI:
    def __init__(self, root, engine, agents=None):
        """
        Parameters
        ----------
        root    : tk.Tk
        engine  : GameManager
        agents  : dict, optional  {player_name: AgentPlayer}
        """
        self.root = root
        self.engine = engine
        self.agents = agents or {}

        # --- Main Layout ---
        self.main_frame = tk.Frame(root, bg="#2b2b2b")
        self.main_frame.pack(fill="both", expand=True)

        # ---- LEFT: Board Canvas ----
        canvas_frame = tk.Frame(self.main_frame, bg="#2b2b2b")
        canvas_frame.pack(side="left", padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_frame, width=600, height=625,
                                bg="#d4a254", highlightthickness=2,
                                highlightbackground="#8B6914")
        self.canvas.pack()

        self._draw_abstract_board()

        # ---- RIGHT: Control Panel ----
        self.panel = tk.Frame(self.main_frame, width=320, bg="#1e1e2e", padx=12)
        self.panel.pack(side="right", fill="y", pady=10)
        self.panel.pack_propagate(False)

        tk.Label(self.panel, text="CLUE!", font=("Arial", 20, "bold"),
                 fg="#f4d03f", bg="#1e1e2e").pack(pady=(15, 5))

        self.lbl_turn = tk.Label(self.panel, text="", font=("Arial", 13, "bold"),
                                 fg="white", bg="#1e1e2e", wraplength=290)
        self.lbl_turn.pack(pady=5)

        self.lbl_status = tk.Label(self.panel, text="Game Started!",
                                   fg="#a8d8ea", bg="#1e1e2e", wraplength=290,
                                   justify="left", font=("Arial", 10))
        self.lbl_status.pack(pady=5)

        # --- Tabbed Interface ---
        self.notebook = ttk.Notebook(self.panel)
        self.notebook.pack(fill="both", expand=True, pady=5)

        self.tab_controls = tk.Frame(self.notebook, bg="#2E3440")
        self.notebook.add(self.tab_controls, text="Controls")

        self.tab_log = tk.Frame(self.notebook, bg="#2E3440")
        self.notebook.add(self.tab_log, text="Game Log")

        self.log_text = tk.Text(self.tab_log, bg="#3B4252", fg="#ECEFF4", font=("Courier", 9), wrap="word",
                                state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        # -----------------------------

        # Parent everything to self.tab_controls instead of self.panel
        ttk.Separator(self.tab_controls, orient="horizontal").pack(fill="x", pady=5)

        btn_kw = {"width": 22, "font": ("Arial", 10, "bold"), "relief": "flat", "cursor": "hand2", "pady": 4}

        self.btn_passage = tk.Button(self.tab_controls, text="Take Secret Passage", command=self.do_passage,
                                     bg="#B48EAD", fg="white", **btn_kw)
        self.btn_roll = tk.Button(self.tab_controls, text="Roll Dice", command=self.do_roll, bg="#BF616A", fg="white",
                                  **btn_kw)
        self.btn_roll.pack(pady=4)

        self.move_var = tk.StringVar()
        self.combo_move = ttk.Combobox(self.tab_controls, textvariable=self.move_var, state="readonly", width=26,
                                       font=("Arial", 9))
        self.combo_move.pack(pady=3)

        self.btn_move = tk.Button(self.tab_controls, text="Confirm Move", command=self.do_move, state="disabled",
                                  bg="#A3BE8C", fg="white", **btn_kw)
        self.btn_move.pack(pady=4)

        ttk.Separator(self.tab_controls, orient="horizontal").pack(fill="x", pady=5)

        self.btn_suggest = tk.Button(self.tab_controls, text="Make Suggestion", command=self.do_suggest,
                                     state="disabled", bg="#5E81AC", fg="white", **btn_kw)
        self.btn_suggest.pack(pady=4)

        self.btn_accuse = tk.Button(self.tab_controls, text="Make Accusation", command=self.do_accuse, bg="#D08770",
                                    fg="white", **btn_kw)
        self.btn_accuse.pack(pady=4)

        self.btn_end = tk.Button(self.tab_controls, text="End Turn", command=self.do_end_turn, bg="#4C566A", fg="white",
                                 **btn_kw)
        self.btn_end.pack(pady=10)

        ttk.Separator(self.tab_controls, orient="horizontal").pack(fill="x", pady=5)

        tk.Label(self.tab_controls, text="Your Cards", font=("Arial", 10, "bold"), fg="#EBCB8B", bg="#2E3440").pack()
        self.lbl_cards = tk.Label(self.tab_controls, text="", fg="#ECEFF4", bg="#2E3440", font=("Courier", 9),
                                  justify="left", wraplength=290)
        self.lbl_cards.pack(pady=3)

        self.lbl_cards.bind("<Enter>", self._on_hover_cards_enter)
        self.lbl_cards.bind("<Leave>", self._on_hover_cards_leave)

        ttk.Separator(self.tab_controls, orient="horizontal").pack(fill="x", pady=5)

        tk.Label(self.tab_controls, text="Detective Notes", font=("Arial", 10, "bold"), fg="#EBCB8B",
                 bg="#2E3440").pack()
        self.lbl_notes = tk.Label(self.tab_controls, text="None yet", fg="#D8DEE9", bg="#2E3440", font=("Courier", 8),
                                  justify="left", wraplength=290)
        self.lbl_notes.pack(pady=3)

        self.refresh_ui()

    def stairs(self, x, y, to_room):
        c = self.canvas
        c.create_rectangle(x, y - 1, x - CELL / 2, y - CELL, fill="#A88213", outline="", tags="stairs")
        c.create_rectangle(x + (CELL / 2), y - 1, x, y - CELL, fill="#917114", outline="", tags="stairs")
        c.create_rectangle(x + CELL, y - 1, x + CELL / 2, y - CELL, fill="#634D0B", outline="", tags="stairs")
        c.create_rectangle(x + (CELL * 1.5), y - 1, x + CELL, y - CELL, fill="#332805", outline="", tags="stairs")
        self.canvas.create_text(
            x+CELL*0.5, y - CELL,
            text=f"Passage to {to_room}",
            fill="#FFFFFF",
            font=("Arial", 7)
        )

    def log_event(self, message):
        """Appends text to the Game Log tab and auto-scrolls to the bottom."""
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _on_hover_cards_enter(self, event):
        """Reveals the cards when the mouse hovers over the label."""
        player = self.engine.get_current_player()
        if player.name not in self.agents and hasattr(self, "_current_human_cards_text"):
            self.lbl_cards.config(text=self._current_human_cards_text)

    def _on_hover_cards_leave(self, event):
        """Hides the cards when the mouse leaves the label."""
        player = self.engine.get_current_player()
        if player.name not in self.agents:
            self.lbl_cards.config(text="  [Hover to reveal cards]")

    # ------------------------------------------------------------------
    # Board rendering
    # ------------------------------------------------------------------

    def _draw_abstract_board(self):
        c = self.canvas
        # Sleek dark background
        c.create_rectangle(0, 0, 600, 625, fill="#2E3440", outline="")

        # Draw precise grid lines
        for i in range(0, 625, CELL):
            c.create_line(i, 0, i, 625, fill="#4C566A", stipple="gray50")
            c.create_line(0, i, 600, i, fill="#4C566A", stipple="gray50")

        # Dynamically draw rooms based on JSON bounds
        room_bounds = self.engine.board.grid.get("room_bounds", [])
        for bounds in room_bounds:
            room_name = bounds["room"]
            px1 = bounds["x1"] * CELL
            py1 = bounds["y1"] * CELL
            px2 = (bounds["x2"] + 1) * CELL
            py2 = (bounds["y2"] + 1) * CELL

            c.create_rectangle(px1, py1, px2, py2,
                               fill="#3B4252", outline="#88C0D0", width=2)

            cx = (px1 + px2) / 2
            cy = (py1 + py2) / 2
            c.create_text(cx, cy, text=room_name, fill="#ECEFF4", font=("Arial", 9, "bold"))

        # Draw doors dynamically from JSON
        doors = self.engine.board.grid.get("doors", [])
        for door in doors:
            col, row = door["grid_coord"]
            px, py = coord_to_pixel((col, row))
            c.create_rectangle(px - 10, py - 10, px + 10, py + 10,
                               fill="#A3BE8C", outline="#2E3440", width=2)

        c.create_text(300, 300, text="CLUE!", fill="#EBCB8B", font=("Arial", 24, "bold"))

        # DRAW AXIS LABELS LAST SO THEY RENDER ON TOP

        # X-axis (Top edge): 24 columns, from 0 to 23
        for i in range(24):
            c.create_text(i * CELL + CELL // 2, 8, text=str(i), fill="#88C0D0", font=("Arial", 6))

        # Y-axis (Left edge): 25 rows, from 1 to 24 (skipping 0 to avoid top-left corner clutter)
        for i in range(1, 25):
            c.create_text(8, i * CELL + CELL // 2, text=str(i), fill="#88C0D0", font=("Arial", 6))


        # MAKE STAIRS FOR PASSAGES
        self.stairs(CELL * 2, CELL * 5, "Kitchen")
        self.stairs(CELL * 21.5, CELL * 2, "Conservatory")
        self.stairs(CELL * 2, CELL * 25, "Lounge")
        self.stairs(CELL * 22, CELL * 25, "Study")


    def _draw_tokens(self):
        self.canvas.delete("token")
        room_offsets = {}

        for player in self.engine.players:
            loc = player.location
            colour = PLAYER_COLOURS.get(player.name, "#ffffff")
            if loc is None:
                continue

            if isinstance(loc, str):
                # Dynamically find the center of the room from JSON
                room_bounds = self.engine.board.grid.get("room_bounds", [])
                base_x, base_y = 300, 300  # Default fallback
                for bounds in room_bounds:
                    if bounds["room"] == loc:
                        base_x = (bounds["x1"] + bounds["x2"] + 1) * CELL / 2
                        base_y = (bounds["y1"] + bounds["y2"] + 1) * CELL / 2
                        break

                idx = room_offsets.get(loc, 0)
                room_offsets[loc] = idx + 1
                offset_x = (idx % 3) * 18 - 18
                offset_y = (idx // 3) * 18 - 9
                cx, cy = base_x + offset_x, base_y + offset_y
            else:
                cx, cy = coord_to_pixel(loc)

            r = 9
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    fill=colour, outline="#111", width=2,
                                    tags="token")
            initials = "".join(w[0] for w in player.name.split()[:2])
            self.canvas.create_text(cx, cy, text=initials,
                                    font=("Arial", 6, "bold"),
                                    fill="#111" if colour != "#1e1e2e" else "#fff",
                                    tags="token")

    def _draw_grid_and_doors(self):
        """Draws a visual grid and highlights door coordinates from the JSON."""
        c = self.canvas

        # 1. Draw a faint grid
        for i in range(0, 625, CELL):
            # Vertical lines
            c.create_line(i, 0, i, 625, fill="#ffffff", stipple="gray50", tags="overlay")
            # Horizontal lines
            c.create_line(0, i, 600, i, fill="#ffffff", stipple="gray50", tags="overlay")

        # 2. Draw the doors
        doors = self.engine.board.grid.get("doors", [])
        for door in doors:
            col, row = door["grid_coord"]
            px, py = coord_to_pixel((col, row))

            # Draw a bright green square for the door
            c.create_rectangle(px - 10, py - 10, px + 10, py + 10,
                               fill="#2a9d8f", outline="white", width=2, tags="overlay")
            c.create_text(px, py, text="DOOR", font=("Arial", 5, "bold"),
                          fill="white", tags="overlay")

    # ------------------------------------------------------------------
    # UI refresh
    # ------------------------------------------------------------------

    def refresh_ui(self):
        player = self.engine.get_current_player()
        is_agent = player.name in self.agents

        self.lbl_turn.config(
            text=f"{'[AI] ' if is_agent else ''}{player.name}'s Turn"
        )

        # Secret passage button
        passage = self.engine.get_available_passage()
        if passage and not is_agent:
            self.btn_passage.config(text=f"Take Passage to {passage}")
            self.btn_passage.pack(pady=4, before=self.btn_roll)
        else:
            self.btn_passage.pack_forget()

        # Card hand (human players only)
        if not is_agent:
            # Save the real text to a variable, but display the hidden text
            self._current_human_cards_text = "\n".join(
                f"  [{c.card_type[0]}] {c.name}" for c in player.held_cards
            ) or "  (No cards)"
            self.lbl_cards.config(text="  [Hover to reveal cards]")
        else:
            self._current_human_cards_text = "  (AI — hidden)"
            self.lbl_cards.config(text="  (AI — hidden)")

        # Detective notes
        if not hasattr(player, "known_innocent"):
            player.known_innocent = set()
        if player.known_innocent:
            self.lbl_notes.config(
                text="\n".join(f"  X {c}" for c in sorted(player.known_innocent))
            )
        else:
            self.lbl_notes.config(text="  None yet")

        # Reset controls
        self.btn_roll.config(state="normal" if not is_agent else "disabled")
        self.combo_move.config(state="readonly")
        self.combo_move.set('')
        self.combo_move['values'] = []
        self.btn_move.config(state="disabled")
        self.btn_suggest.config(state="disabled")

        if not is_agent and self.engine.board.is_room(player.location):
            self.btn_suggest.config(state="normal")
        else:
            self.btn_suggest.config(state="disabled")

        self._draw_tokens()

        # Trigger AI automatically
        if is_agent:
            self.root.after(1200, self._run_agent_turn)

    # ------------------------------------------------------------------
    # Human player actions
    # ------------------------------------------------------------------

    def coords_highlight(self, valid_moves):
        c = self.canvas
        for i in range (len(valid_moves)):
            c.create_rectangle(valid_moves[i][0]*CELL, valid_moves[i][1]*CELL, (valid_moves[i][0]+1)*CELL, (valid_moves[i][1]+1)*CELL, fill="#0AFA1E", outline="", tags="highlight")
            self.canvas.create_text(
                valid_moves[i][0]*CELL + (CELL/2), valid_moves[i][1]*CELL + (CELL/2),
                text=str(valid_moves[i]),
                fill="#2E3440",
                font=("Arial", 5)
            )


    def do_passage(self):
        dest = self.engine.handle_passage()
        if dest:
            self.lbl_status.config(text=f"Took secret passage to {dest}!")
            self.btn_passage.pack_forget()
            self.btn_roll.config(state="disabled")
            player = self.engine.get_current_player()
            if self.engine.board.is_room(player.location):
                self.btn_suggest.config(state="normal")
            self._draw_tokens()

    def do_roll(self):
        roll, valid_moves = self.engine.handle_roll()
        self.lbl_status.config(text=f"Rolled a {roll}! Choose destination.")

        self.btn_suggest.config(state="disabled")

        if valid_moves:
            # Build a map of door coordinates to room names from the JSON
            door_map = {tuple(d["grid_coord"]): d["room"] for d in self.engine.board.grid.get("doors", [])}

            display_values = []
            for m in valid_moves:
                if m in door_map:
                    # Append the room name if the coordinate is a door
                    display_values.append(f"{m} -> Enter {door_map[m]}")
                else:
                    display_values.append(str(m))

            self.combo_move['values'] = display_values
            self.combo_move.current(0)
            self.btn_move.config(state="normal")
            self.combo_move.configure(values=sorted(display_values))
        else:
            self.lbl_status.config(text=f"Rolled {roll} — no valid moves.")

        self.btn_roll.config(state="disabled")
        self.btn_passage.pack_forget()
        self.coords_highlight(valid_moves)



    def do_move(self):
        self.canvas.delete("highlight")
        chosen = self.move_var.get()
        if not chosen:
            return

        # Parse the coordinate out, ignoring our custom "Enter Room" text
        coord_str = chosen.split(" ->")[0]
        if coord_str.startswith("("):
            dest_coord = eval(coord_str)
        else:
            dest_coord = coord_str

        # If they stepped onto a door, move them entirely INTO the room string
        door_map = {tuple(d["grid_coord"]): d["room"] for d in self.engine.board.grid.get("doors", [])}
        if dest_coord in door_map:
            final_dest = door_map[dest_coord]
            self.lbl_status.config(text=f"Entered the {final_dest}.")
        else:
            final_dest = dest_coord
            self.lbl_status.config(text=f"Moved to {final_dest}.")

        self.engine.handle_move(final_dest)

        player = self.engine.get_current_player()
        self.btn_move.config(state="disabled")
        self.combo_move.config(state="disabled")

        if self.engine.board.is_room(player.location):
            self.btn_suggest.config(state="normal")

        self._draw_tokens()
        self.btn_roll.config(state="disabled")

    def do_suggest(self):
        player = self.engine.get_current_player()
        persons = ["Miss Scarlett", "Col Mustard", "Mrs White",
                   "Rev Green", "Mrs Peacock", "Prof Plum"]
        weapons = ["Dagger", "Candlestick", "Revolver",
                   "Rope", "Lead Piping", "Spanner"]

        win = tk.Toplevel(self.root)
        win.title("Make a Suggestion")
        win.geometry("320x210")
        win.grab_set()

        tk.Label(win, text=f"Room: {player.location}",
                 font=("Arial", 11, "bold")).pack(pady=8)

        person_var = tk.StringVar(value=persons[0])
        weapon_var = tk.StringVar(value=weapons[0])

        tk.Label(win, text="Suspect:").pack()
        ttk.Combobox(win, textvariable=person_var, values=persons,
                     state="readonly", width=25).pack(pady=2)
        tk.Label(win, text="Weapon:").pack()
        ttk.Combobox(win, textvariable=weapon_var, values=weapons,
                     state="readonly", width=25).pack(pady=2)

        def confirm():
            p, w = person_var.get(), weapon_var.get()
            win.destroy()
            result_card = self.engine.handle_suggestion(p, w)
            if result_card:
                messagebox.showinfo("Suggestion Disproved",
                                    f"Someone showed you: {result_card.name}")
                if not hasattr(player, "known_innocent"):
                    player.known_innocent = set()
                player.known_innocent.add(result_card.name)
                if not hasattr(player, "known_innocent"):
                    player.known_innocent = set()
                self.lbl_notes.config(
                    text="\n".join(f"  X {c}" for c in sorted(player.known_innocent))
                )
            else:
                messagebox.showinfo("Suggestion",
                                    "No one could disprove your suggestion!")
            self.btn_suggest.config(state="disabled")

        tk.Button(win, text="Suggest", command=confirm,
                  bg="#457b9d", fg="white", width=15).pack(pady=10)

    def do_accuse(self):
        persons = ["Miss Scarlett", "Col Mustard", "Mrs White",
                   "Rev Green", "Mrs Peacock", "Prof Plum"]
        weapons = ["Dagger", "Candlestick", "Revolver",
                   "Rope", "Lead Piping", "Spanner"]
        rooms = ["Hall", "Lounge", "Dining Room", "Kitchen", "Ball Room",
                 "Conservatory", "Billiard Room", "Library", "Study"]

        win = tk.Toplevel(self.root)
        win.title("Make an Accusation")
        win.geometry("340x260")
        win.grab_set()

        tk.Label(win, text="This is your FINAL accusation!",
                 font=("Arial", 11, "bold"), fg="red").pack(pady=8)

        person_var = tk.StringVar(value=persons[0])
        weapon_var = tk.StringVar(value=weapons[0])
        room_var = tk.StringVar(value=rooms[0])

        for label, var, opts in [("Suspect:", person_var, persons),
                                 ("Weapon:", weapon_var, weapons),
                                 ("Room:", room_var, rooms)]:
            tk.Label(win, text=label).pack()
            ttk.Combobox(win, textvariable=var, values=opts,
                         state="readonly", width=25).pack(pady=2)

        def confirm():
            p, w, r = person_var.get(), weapon_var.get(), room_var.get()
            win.destroy()
            won = self.engine.handle_accusation(p, w, r)
            if won:
                messagebox.showinfo("WINNER!",
                                    f"Correct!\n{p} with the {w} in the {r}!")
                self.root.destroy()
            else:
                messagebox.showerror("Wrong Accusation",
                                     "Incorrect! You can no longer take turns,\n"
                                     "but you still disprove suggestions.")
                self.do_end_turn()

        tk.Button(win, text="Accuse!", command=confirm,
                  bg="#e63946", fg="white", width=15).pack(pady=10)

    def do_end_turn(self):
        self.engine.end_turn()
        self.lbl_status.config(text="Waiting for roll...")
        self.combo_move.config(state="readonly")
        self.refresh_ui()

    # ------------------------------------------------------------------
    # AI agent turn
    # ------------------------------------------------------------------

    def _run_agent_turn(self):
        player = self.engine.get_current_player()
        agent = self.agents.get(player.name)

        if not agent or self.engine.game_over:
            return

        self.lbl_status.config(text=f"[AI] {player.name} is thinking...")
        self.root.update()

        log = agent.execute_turn(self.engine)

        self.lbl_status.config(text=f"[AI] {player.name} finished their turn.")

        # Write AI actions clearly into the history tab
        self.log_event(f"--- {player.name}'s Turn (AI) ---")
        for action in log.get("actions", []):
            self.log_event(f"  • {action}")
        self.log_event("")

        if log.get("won") is True:
            messagebox.showinfo("Game Over",
                                f"[AI] {player.name} solved the mystery and won!")
            self.root.destroy()
            return
        elif log.get("won") is False:
            messagebox.showwarning("AI Accusation",
                                   f"{player.name} made a wrong accusation.")

        self._draw_tokens()
        self.root.after(800, self.refresh_ui)
