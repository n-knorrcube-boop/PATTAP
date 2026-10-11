import random
import tkinter as tk
from tkinter import *
from tkinter import messagebox

GRID_SIZE = 4
TOTAL_ROUNDS = 3
LETTER_SEQUENCE = ("A", "P", "T")   # single shared sequence


# --- GAME LOGIC ---

class PatTapGame:
    def __init__(self):
        self.scores = [0, 0]
        self.round_number = 0
        self.new_round()

    def new_round(self):
        """Prepare a fresh grid and reset the shared letter sequence."""
        self.grid = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.placed_by = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]

        self.sequence_index = 0

        self.current_player = 0
        self.round_number += 1
        self.round_over = False
        self.game_over = False
        self.winner = None

    def get_next_letter(self):
        return LETTER_SEQUENCE[self.sequence_index % len(LETTER_SEQUENCE)]

    def place_letter(self, row, col):
        if self.game_over or self.round_over:
            return {"success": False, "message": "Round is over."}

        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return {"success": False, "message": "Invalid position."}

        if self.grid[row][col] is not None:
            return {"success": False, "message": "Cell is occupied."}

        player = self.current_player
        letter = self.get_next_letter()

        self.grid[row][col] = letter
        self.placed_by[row][col] = player

        self.sequence_index += 1

        result = self.check_winner()

        if result:
            word, owner = result
            self.scores[owner] += 1
            self.round_over = True

            if self.round_number >= TOTAL_ROUNDS:
                self.game_over = True
                if self.scores[0] > self.scores[1]:
                    self.winner = 0
                elif self.scores[1] > self.scores[0]:
                    self.winner = 1
                else:
                    self.winner = -1

            return {
                "success": True, "letter": letter, "player": player,
                "word": word, "point_to": owner, "scores": self.scores[:],
                "round_over": True, "game_over": self.game_over,
                "winner": self.winner,
            }

        self.current_player = 1 - player

        if all(cell is not None for row in self.grid for cell in row):
            self.round_over = True

            if self.round_number >= TOTAL_ROUNDS:
                self.game_over = True
                self.winner = (
                    0 if self.scores[0] > self.scores[1]
                    else 1 if self.scores[1] > self.scores[0]
                    else -1
                )

            return {
                "success": True, "letter": letter, "player": player,
                "word": None, "point_to": None, "scores": self.scores[:],
                "round_over": True, "game_over": self.game_over,
                "winner": self.winner,
            }

        return {
            "success": True, "letter": letter, "player": player,
            "word": None, "point_to": None, "scores": self.scores[:],
            "round_over": False, "game_over": False, "winner": None,
        }

    def check_winner(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if col + 2 < GRID_SIZE:
                    cells = [(row, col + o) for o in range(3)]
                    letters = "".join(self.grid[r][c] or "" for r, c in cells)
                    if letters in ("PAT", "TAP"):
                        return letters, self.placed_by[cells[2][0]][cells[2][1]]

                if row + 2 < GRID_SIZE:
                    cells = [(row + o, col) for o in range(3)]
                    letters = "".join(self.grid[r][c] or "" for r, c in cells)
                    if letters in ("PAT", "TAP"):
                        return letters, self.placed_by[cells[2][0]][cells[2][1]]

        return None

    def get_final_result(self):
        if not self.game_over:
            return "Game is not finished."
        if self.winner == -1:
            return "The game is a tie!"
        return f"Player {self.winner + 1} wins!"


# --- STATE ---

game = None
game_mode = None


# --- UI HELPERS ---

def refresh_ui():
    if game is None:
        return

    round_label.config(text=f"Round {game.round_number} / {TOTAL_ROUNDS}")

    score_label.config(
        text=(f"Player 1: {game.scores[0]}     "
              f"Player 2: {game.scores[1]}")
    )

    turn = game.current_player + 1
    next_letter = game.get_next_letter()
    turn_label.config(
        text=f"Player {turn}'s turn - CURRENT LETTER: {next_letter}"
    )

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            letter = game.grid[r][c]
            owner = game.placed_by[r][c]
            btn = buttons[r][c]
            btn.config(text=letter or "")

            if owner == 0:
                btn.config(fg="#1f6feb")
            elif owner == 1:
                btn.config(fg="#d7263d")
            else:
                btn.config(fg="black")

    if game.round_over and not game.game_over:
        next_button.config(state=NORMAL)
    else:
        next_button.config(state=DISABLED)


# --- SCREEN SWITCHING ---

def start_game(selected_mode):
    global game, game_mode
    game_mode = selected_mode
    game = PatTapGame()

    menu_frame.pack_forget()
    tutorial_frame.pack_forget()
    game_frame.pack(fill=BOTH, expand=True)

    refresh_ui()


def back_to_menu():
    game_frame.pack_forget()
    tutorial_frame.pack_forget()
    menu_frame.pack(fill=BOTH, expand=True)


def show_tutorial():
    menu_frame.pack_forget()
    game_frame.pack_forget()
    tutorial_frame.pack(fill=BOTH, expand=True)
    # Reset scroll to top whenever the tutorial is opened
    tutorial_canvas.yview_moveto(0)


def close_tutorial():
    tutorial_frame.pack_forget()
    menu_frame.pack(fill=BOTH, expand=True)


# --- EVENT HANDLERS ---

def on_click(row, column):
    if game is None:
        return
    if game.round_over or game.game_over:
        return

    result = game.place_letter(row, column)
    if not result["success"]:
        return

    refresh_ui()

    if result["word"]:
        messagebox.showinfo(
            "Word formed!",
            f"{result['word']} formed!\n"
            f"Point goes to Player {result['point_to'] + 1}."
        )

    if result["game_over"]:
        messagebox.showinfo(
            "Game over",
            f"Final scores:\n"
            f"Player 1: {game.scores[0]}\n"
            f"Player 2: {game.scores[1]}\n\n"
            f"{game.get_final_result()}"
        )


def next_action():
    if game is None:
        return
    if not (game.round_over and not game.game_over):
        return
    game.new_round()
    refresh_ui()


def _on_mousewheel(event):
    """Windows / macOS mouse wheel scroll."""
    tutorial_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def _on_mousewheel_linux(event):
    """Linux mouse wheel scroll (Button-4 / Button-5)."""
    if event.num == 4:
        tutorial_canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        tutorial_canvas.yview_scroll(1, "units")


# --- WINDOW ---

window = Tk()
window.title("PAT/TAP")
window.geometry("460x560")

# ---------- INTRO / MENU SCREEN ----------
menu_frame = Frame(window)
menu_frame.pack(fill=BOTH, expand=True)

Label(menu_frame, text="PAT/TAP", font=("Arial", 44, "bold")).pack(pady=(70, 40))

Button(menu_frame, text="Solo", font=("Arial", 18), width=14,
       command=lambda: start_game("solo")).pack(pady=8)
Button(menu_frame, text="Pass & Play", font=("Arial", 18), width=14,
       command=lambda: start_game("pass")).pack(pady=8)
Button(menu_frame, text="Tutorial", font=("Arial", 18), width=14,
       command=show_tutorial).pack(pady=8)


# --- TUTORIAL SCREEN ---

tutorial_frame = Frame(window)

# Canvas + vertical scrollbar
tutorial_canvas = Canvas(tutorial_frame, highlightthickness=0)
tutorial_scrollbar = Scrollbar(tutorial_frame, orient="vertical",
                               command=tutorial_canvas.yview)
tutorial_canvas.configure(yscrollcommand=tutorial_scrollbar.set)

tutorial_scrollbar.pack(side="right", fill="y")
tutorial_canvas.pack(side="left", fill=BOTH, expand=True)

# Inner frame that holds all the tutorial content
tutorial_content = Frame(tutorial_canvas)

# Put the inner frame into the canvas as a window
tutorial_window_id = tutorial_canvas.create_window(
    (0, 0), window=tutorial_content, anchor="nw"
)


def _resize_tutorial_content(event):
    """Make the inner frame stretch to the canvas width."""
    tutorial_canvas.itemconfig(tutorial_window_id, width=event.width)


def _update_scrollregion(event):
    """Keep the scrollable region sized to the inner frame."""
    tutorial_canvas.configure(scrollregion=tutorial_canvas.bbox("all"))


tutorial_content.bind("<Configure>", _update_scrollregion)
tutorial_canvas.bind("<Configure>", _resize_tutorial_content)

# Mouse-wheel bindings (all platforms)
tutorial_canvas.bind_all("<MouseWheel>", _on_mousewheel)         # Win / Mac
tutorial_canvas.bind_all("<Button-4>", _on_mousewheel_linux)     # Linux up
tutorial_canvas.bind_all("<Button-5>", _on_mousewheel_linux)     # Linux down


# ---------- Tutorial content (goes inside tutorial_content) ----------

Label(tutorial_content, text="HOW TO PLAY",
      font=("Arial", 22, "bold")).pack(pady=(15, 5))

# --- Section 1: The target words ---
Label(tutorial_content, text="1. Build one of these words in order:",
      font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 4))

words_frame = Frame(tutorial_content)
words_frame.pack(pady=2)

def word_row(parent, letters, label_text):
    row = Frame(parent)
    row.pack(pady=3)
    Label(row, text=label_text, font=("Arial", 11, "bold"),
          width=12, anchor="w").pack(side="left")
    for i, ch in enumerate(letters):
        Label(row, text=ch, font=("Arial", 18, "bold"),
              width=3, height=1, relief="ridge", borderwidth=2,
              bg="#f0f0f0").pack(side="left", padx=2)
        if i < len(letters) - 1:
            Label(row, text="→", font=("Arial", 14)).pack(side="left", padx=1)

word_row(words_frame, "PAT", "Word A:")
word_row(words_frame, "TAP", "Word B:")

Label(tutorial_content,
      text="The letters must appear in this exact order,\n"
           "read either left-to-right or top-to-bottom.",
      font=("Arial", 10, "italic"), fg="#555555").pack(pady=(2, 6))


# --- Section 2: Shared letter sequence ---
Label(tutorial_content, text="2. Letters drop into the grid in this cycle:",
      font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))

seq_frame = Frame(tutorial_content)
seq_frame.pack(pady=4)

def letter_box(parent, letter):
    Label(parent, text=letter, font=("Arial", 20, "bold"),
          width=3, height=1, relief="ridge", borderwidth=2,
          bg="#f0f0f0").pack(side="left", padx=4)

letter_box(seq_frame, "A")
Label(seq_frame, text="→", font=("Arial", 16)).pack(side="left", padx=2)
letter_box(seq_frame, "P")
Label(seq_frame, text="→", font=("Arial", 16)).pack(side="left", padx=2)
letter_box(seq_frame, "T")
Label(seq_frame, text="→", font=("Arial", 16)).pack(side="left", padx=2)
letter_box(seq_frame, "A")
Label(seq_frame, text="…", font=("Arial", 16)).pack(side="left", padx=2)

Label(tutorial_content,
      text="Players take turns placing the next letter\n"
           "wherever they want on the board.",
      font=("Arial", 10, "italic"), fg="#555555").pack(pady=(2, 6))


# --- Section 3: PAT horizontally ---
Label(tutorial_content, text="3. Example — PAT formed horizontally:",
      font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))

example_pat = Frame(tutorial_content)
example_pat.pack(pady=4)

sample_pat = [
    ["P", "A", "T", ""],
    ["",  "",  "",  ""],
    ["",  "",  "",  ""],
    ["",  "",  "",  ""],
]
sample_pat_colors = [
    ["#1f6feb", "#d7263d", "#1f6feb", "black"],
    ["black", "black", "black", "black"],
    ["black", "black", "black", "black"],
    ["black", "black", "black", "black"],
]
for r in range(4):
    for c in range(4):
        Label(example_pat, text=sample_pat[r][c], fg=sample_pat_colors[r][c],
              width=3, height=1, font=("Arial", 16, "bold"),
              relief="ridge", borderwidth=1, bg="#f0f0f0").grid(row=r, column=c)


# --- Section 4: TAP vertically ---
Label(tutorial_content, text="4. Example — TAP formed vertically:",
      font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))

example_tap = Frame(tutorial_content)
example_tap.pack(pady=4)

sample_tap = [
    ["T", "",  "",  ""],
    ["A", "",  "",  ""],
    ["P", "",  "",  ""],
    ["",  "",  "",  ""],
]
sample_tap_colors = [
    ["#1f6feb", "black", "black", "black"],
    ["#d7263d", "black", "black", "black"],
    ["#1f6feb", "black", "black", "black"],
    ["black", "black", "black", "black"],
]
for r in range(4):
    for c in range(4):
        Label(example_tap, text=sample_tap[r][c], fg=sample_tap_colors[r][c],
              width=3, height=1, font=("Arial", 16, "bold"),
              relief="ridge", borderwidth=1, bg="#f0f0f0").grid(row=r, column=c)

Label(tutorial_content,
      text="Blue = Player 1    Red = Player 2",
      font=("Arial", 10, "italic"), fg="#555555").pack(pady=(2, 4))


# --- Section 5: Scoring ---
Label(tutorial_content, text="5. Scoring:",
      font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(8, 2))

Label(tutorial_content,
      text=("The point goes to whoever placed the LAST (3rd)\n"
            "letter that completed the word.\n"
            "In the examples above, Player 1 placed the final letter."),
      font=("Arial", 10), fg="#333333").pack(pady=(0, 10))


# --- Back button ---
Button(tutorial_content, text="Back to Menu", font=("Arial", 14),
       command=close_tutorial).pack(pady=(4, 20))

# --- GAME SCREEN ----

game_frame = Frame(window)

round_label = Label(game_frame, text="Round 1 / 3", font=("Arial", 16, "bold"))
round_label.pack(pady=(10, 0))

score_label = Label(game_frame, text="Player 1: 0     Player 2: 0", font=("Arial", 13))
score_label.pack()

turn_label = Label(game_frame, text="Player 1's turn - CURRENT LETTER: A",
                   font=("Arial", 15), height=2)
turn_label.pack(pady=5)

board_frame = Frame(game_frame)
board_frame.pack()

buttons = [[None] * 4 for _ in range(4)]
for row in range(4):
    for column in range(4):
        buttons[row][column] = Button(
            board_frame, text="", font=("Arial", 18, "bold"), width=4, height=2,
            command=lambda row=row, column=column: on_click(row, column))
        buttons[row][column].grid(row=row, column=column)

bottom_bar = Frame(game_frame)
bottom_bar.pack(side=BOTTOM, pady=12)

next_button = Button(bottom_bar, text="Next Round", font=("Arial", 14),
                     state=DISABLED, command=next_action)
next_button.pack(side=LEFT, padx=6)

Button(bottom_bar, text="Menu", font=("Arial", 14),
       command=back_to_menu).pack(side=LEFT, padx=6)

window.mainloop()