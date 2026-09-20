import random
import tkinter as tk
from tkinter import messagebox


FLASHCARDS = {
    "What is the capital of France?": "Paris",
    "What is the largest planet in our solar system?": "Jupiter",
    "Which programming language is named after a British comedy troupe?": "Python",
    "What is the square root of 64?": "8",
    "What element does 'O' represent on the periodic table?": "Oxygen",
}


class FlashcardApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Python Flashcard App")
        self.root.geometry("500x350")
        self.root.config(bg="#f0f0f0")

        self.questions = list(FLASHCARDS)
        self.current_question = ""
        self.is_showing_answer = False

        self.card_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        self.card_frame.pack(pady=40, padx=20, fill="both", expand=True)

        self.card_label = tk.Label(
            self.card_frame,
            text="",
            font=("Arial", 16, "bold"),
            bg="white",
            wraplength=400,
            justify="center",
        )
        self.card_label.pack(expand=True)

        self.button_frame = tk.Frame(root, bg="#f0f0f0")
        self.button_frame.pack(pady=20)

        self.flip_btn = tk.Button(
            self.button_frame,
            text="Flip Card",
            command=self.flip_card,
            font=("Arial", 12),
            bg="#007bff",
            fg="white",
            padx=10,
        )
        self.flip_btn.grid(row=0, column=0, padx=10)

        self.next_btn = tk.Button(
            self.button_frame,
            text="Next Card",
            command=self.next_card,
            font=("Arial", 12),
            bg="#28a745",
            fg="white",
            padx=10,
        )
        self.next_btn.grid(row=0, column=1, padx=10)

        self.next_card()

    def next_card(self) -> None:
        """Select a random question and update the interface."""
        if not self.questions:
            messagebox.showinfo(
                "Deck complete",
                "You have reviewed all the cards. The deck will restart.",
            )
            self.questions = list(FLASHCARDS)

        self.current_question = random.choice(self.questions)
        self.questions.remove(self.current_question)
        self.card_label.config(text=self.current_question, fg="black", bg="white")
        self.card_frame.config(bg="white")
        self.is_showing_answer = False

    def flip_card(self) -> None:
        """Toggle between displaying the question and its answer."""
        if not self.is_showing_answer:
            answer = FLASHCARDS[self.current_question]
            self.card_label.config(text=answer, fg="#d9534f", bg="#fff3cd")
            self.card_frame.config(bg="#fff3cd")
            self.is_showing_answer = True
        else:
            self.card_label.config(text=self.current_question, fg="black", bg="white")
            self.card_frame.config(bg="white")
            self.is_showing_answer = False


if __name__ == "__main__":
    main_window = tk.Tk()
    FlashcardApp(main_window)
    main_window.mainloop()
