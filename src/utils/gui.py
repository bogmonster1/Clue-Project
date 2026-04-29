from tkinter import *
from PIL import Image, ImageTk

class GUI:
    def __init__(self, root, engine):
        self.root = root
        self.engine = engine

        # 1. Setup the Canvas
        self.canvas = Canvas(root, width=800, height=800)
        self.canvas.pack()

        # 2. Load the Board Image
        raw_image = Image.open("src/assets/clueboard.jpeg")
        resized_image = raw_image.resize((800, 800))
        self.board_bg = ImageTk.PhotoImage(resized_image)

        # 3. Draw the background
        self.canvas.create_image(0, 0, anchor=NW, image=self.board_bg)

    def draw_tokens(self):
        """Called whenever the engine says a move happened."""
        # Loop through engine.board.piece_locations and draw tokens on top of the canvas
        pass




