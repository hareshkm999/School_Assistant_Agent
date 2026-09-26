import tkinter as tk
from tkinter import messagebox
import random

class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Kids Animal Memory Game 🐼")
        self.root.geometry("450x550")
        self.root.configure(bg="#F0F8FF") # Alice Blue background

        # Available animal emojis for matching
        self.animals = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"]
        # Double the list to make pairs and shuffle
        self.grid_items = self.animals * 2
        random.shuffle(self.grid_items)

        self.buttons = []
        self.clicked_buttons = []
        self.matched_pairs = 0
        self.moves = 0

        # Title Label
        self.title_label = tk.Label(
            self.root, 
            text="Find the Matching Pairs!", 
            font=("Arial", 16, "bold"), 
            bg="#F0F8FF", 
            fg="#333333"
        )
        self.title_label.pack(pady=15)

        # Score / Move Counter Label
        self.score_label = tk.Label(
            self.root, 
            text="Moves: 0", 
            font=("Arial", 12), 
            bg="#F0F8FF", 
            fg="#555555"
        )
        self.score_label.pack(pady=5)

        # Create a grid frame for the buttons
        self.grid_frame = tk.Frame(self.root, bg="#F0F8FF")
        self.grid_frame.pack(expand=True, pady=10)

        # Generate 4x4 Grid of Buttons
        for i in range(16):
            btn = tk.Button(
                self.grid_frame, 
                text="❓", 
                font=("Arial", 22), 
                width=4, 
                height=2, 
                bg="#FFD700", # Gold colored card back
                activebackground="#FFA500",
                command=lambda idx=i: self.on_card_click(idx)
            )
            # Arrange in 4 rows and 4 columns
            btn.grid(row=i // 4, column=i % 4, padx=8, pady=8)
            self.buttons.append(btn)

    def on_card_click(self, idx):
        # Ignore clicks on already revealed or matched buttons
        if idx in self.clicked_buttons or self.buttons[idx]["text"] != "❓":
            return
        
        # Prevent picking more than 2 cards simultaneously
        if len(self.clicked_buttons) >= 2:
            return

        # Reveal the animal emoji on the clicked card
        self.buttons[idx].config(text=self.grid_items[idx], bg="#FFFFFF")
        self.clicked_buttons.append(idx)

        # If two cards are flipped, evaluate them after a short delay
        if len(self.clicked_buttons) == 2:
            self.moves += 1
            self.score_label.config(text=f"Moves: {self.moves}")
            self.root.after(600, self.check_match)

    def check_match(self):
        idx1, idx2 = self.clicked_buttons

        if self.grid_items[idx1] == self.grid_items[idx2]:
            # It's a match! Disable buttons and turn them green
            self.buttons[idx1].config(bg="#98FB98", state="disabled")
            self.buttons[idx2].config(bg="#98FB98", state="disabled")
            self.matched_pairs += 1
            
            # Check if game is completed
            if self.matched_pairs == len(self.animals):
                messagebox.showinfo(
                    "Congratulations! 🎉", 
                    f"You found all pairs in {self.moves} moves! Great job!"
                )
        else:
            # Not a match, flip them back over
            self.buttons[idx1].config(text="❓", bg="#FFD700")
            self.buttons[idx2].config(text="❓", bg="#FFD700")

        # Reset selection array for the next turn
        self.clicked_buttons = []

if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGame(root)
    root.mainloop()
