import tkinter as tk
import random

GRID_SIZE = 4
TOTAL_ROUNDS = 3
LETTER_SEQUENCE = ("A", "P", "T")


# =========================================================
#  GAME LOGIC — PASS & PLAY
# =========================================================

class PatTapGame:
    def __init__(self):
        self.scores = [0, 0]
        self.round_number = 0
        self.grid = None
        self.placed_by = None
        self.sequence_index = 0
        self.current_player = 0
        self.round_over = False
        self.round_winner = None
        self.game_over = False
        self.match_winner = None
        self.new_round()

    def new_round(self):
        self.grid = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.placed_by = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.sequence_index = 0
        self.current_player = 0
        self.round_number += 1
        self.round_over = False
        self.round_winner = None
        self.game_over = False
        self.match_winner = None

    def get_next_letter(self):
        return LETTER_SEQUENCE[self.sequence_index % len(LETTER_SEQUENCE)]

    def place_letter(self, row, col):
        if self.game_over or self.round_over:
            return False
        if self.grid[row][col] is not None:
            return False

        player = self.current_player
        self.grid[row][col] = self.get_next_letter()
        self.placed_by[row][col] = player
        self.sequence_index += 1

        winner = self.check_winner()
        if winner:
            _, owner = winner
            self.scores[owner] += 1
            self.round_over = True
            self.round_winner = owner
            self._maybe_end_match()
            return True

        self.current_player = 1 - player

        if all(cell is not None for row in self.grid for cell in row):
            self.round_over = True
            self.round_winner = -1
            self._maybe_end_match()
        return True

    def _maybe_end_match(self):
        if self.round_number >= TOTAL_ROUNDS:
            self.game_over = True
            if self.scores[0] > self.scores[1]:
                self.match_winner = 0
            elif self.scores[1] > self.scores[0]:
                self.match_winner = 1
            else:
                self.match_winner = -1

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


# =========================================================
#  GAME LOGIC — SOLO
# =========================================================

class GameAI:
    def __init__(self):
        self.board = [["", "", "", ""] for _ in range(GRID_SIZE)]
        self.placed_by = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.player_sequence = ["A", "T", "P"]
        self.ai_sequence = ["P", "A", "T"]
        self.player_letter_index = 0
        self.ai_letter_index = 0
        self.player_score = 0
        self.ai_score = 0
        self.player_target = ""
        self.ai_target = ""
        self.current_turn = "player"
        self.round_over = False
        self.round_winner = None

    def start_round(self):
        self.board = [["", "", "", ""] for _ in range(GRID_SIZE)]
        self.placed_by = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.player_letter_index = 0
        self.ai_letter_index = 0
        self.current_turn = "player"
        self.round_over = False
        self.round_winner = None
        if random.choice([True, False]):
            self.player_target, self.ai_target = "PAT", "TAP"
        else:
            self.player_target, self.ai_target = "TAP", "PAT"

    def get_player_letter(self):
        return self.player_sequence[self.player_letter_index]

    def get_ai_letter(self):
        return self.ai_sequence[self.ai_letter_index]

    def get_current_letter(self):
        return (self.get_player_letter()
                if self.current_turn == "player"
                else self.get_ai_letter())

    def get_empty_cells(self):
        return [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                if self.board[r][c] == ""]

    def is_board_full(self):
        return not self.get_empty_cells()

    def place_player_letter(self, row, column):
        if self.current_turn != "player" or self.round_over:
            return False
        if self.board[row][column] != "":
            return False

        self.board[row][column] = self.get_player_letter()
        self.placed_by[row][column] = "player"
        self.player_letter_index = (self.player_letter_index + 1) % 3

        winner = self.check_winner()
        if winner:
            self.round_winner = winner
            self.round_over = True
            self.add_score(winner)
            return True
        if self.is_board_full():
            self.round_over = True
            self.round_winner = "tie"
            return True
        self.current_turn = "ai"
        return True

    def check_word(self, target_word):
        for row in range(GRID_SIZE):
            for col in range(2):
                if (self.board[row][col] + self.board[row][col + 1]
                        + self.board[row][col + 2]) == target_word:
                    return True
        for row in range(2):
            for col in range(GRID_SIZE):
                if (self.board[row][col] + self.board[row + 1][col]
                        + self.board[row + 2][col]) == target_word:
                    return True
        return False

    def check_winner(self):
        if self.check_word(self.player_target):
            return "player"
        if self.check_word(self.ai_target):
            return "ai"
        return None

    def choose_ai_move(self):
        empty = self.get_empty_cells()
        if not empty:
            return None
        ai_letter = self.get_ai_letter()

        # 1. Win
        for r, c in empty:
            self.board[r][c] = ai_letter
            if self.check_word(self.ai_target):
                self.board[r][c] = ""
                return r, c
            self.board[r][c] = ""

        # 2. Block
        for r, c in empty:
            self.board[r][c] = ai_letter
            player_wins = self.check_word(self.player_target)
            self.board[r][c] = ""
            if not player_wins:
                return r, c

        # 3. Random
        return random.choice(empty)

    def make_ai_move(self):
        if self.current_turn != "ai" or self.round_over:
            return None
        move = self.choose_ai_move()
        if move is None:
            return None

        row, column = move
        self.board[row][column] = self.get_ai_letter()
        self.placed_by[row][column] = "ai"
        self.ai_letter_index = (self.ai_letter_index + 1) % 3

        winner = self.check_winner()
        if winner:
            self.round_winner = winner
            self.round_over = True
            self.add_score(winner)
        elif self.is_board_full():
            self.round_over = True
            self.round_winner = "tie"
        else:
            self.current_turn = "player"
        return row, column

    def get_board(self):
        return self.board

    def get_scores(self):
        return self.player_score, self.ai_score

    def get_targets(self):
        return self.player_target, self.ai_target

    def get_round_winner(self):
        return self.round_winner

    def add_score(self, winner):
        if winner == "player":
            self.player_score += 1
        elif winner == "ai":
            self.ai_score += 1

    def get_match_winner(self):
        if self.player_score > self.ai_score:
            return "player"
        if self.ai_score > self.player_score:
            return "ai"
        return "tie"


# =========================================================
#  STATE
# =========================================================

game = None
game_mode = None
solo_round = 1


# =========================================================
#  UI HELPERS
# =========================================================

COLOR_P1 = "#1f6feb"
COLOR_P2 = "#d7263d"


def refresh_ui():
    if game is None:
        return
    if game_mode == "pass":
        refresh_pass_ui()
    else:
        refresh_solo_ui()


def refresh_pass_ui():
    round_label.config(text=f"Round {game.round_number} / {TOTAL_ROUNDS}")
    score_label.config(text=f"Player 1: {game.scores[0]}     "
                            f"Player 2: {game.scores[1]}")

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            owner = game.placed_by[r][c]
            btn = buttons[r][c]
            btn.config(text=game.grid[r][c] or "", state=tk.NORMAL)
            btn.config(fg={0: COLOR_P1, 1: COLOR_P2}.get(owner, "black"))

    if game.round_over:
        turn_label.config(text=(
            "Player 1 wins the round!" if game.round_winner == 0
            else "Player 2 wins the round!" if game.round_winner == 1
            else "Round ended in a tie!"
        ))
        disable_board()
        if game.game_over:
            next_button.config(state=tk.DISABLED)
            window.after(800, lambda: show_results(_pass_results_text(),
                                                   game.match_winner))
        else:
            next_button.config(state=tk.NORMAL)
    else:
        turn_label.config(text=f"Player {game.current_player + 1}'s turn - "
                               f"CURRENT LETTER: {game.get_next_letter()}")


def refresh_solo_ui():
    round_label.config(text=f"Round {solo_round} / {TOTAL_ROUNDS}")
    p, a = game.get_scores()
    pt, at = game.get_targets()
    score_label.config(text=f"Player ({pt}): {p}     AI ({at}): {a}")

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            owner = game.placed_by[r][c]
            btn = buttons[r][c]
            btn.config(text=game.board[r][c] or "")
            if owner == "player":
                btn.config(fg=COLOR_P1)
            elif owner == "ai":
                btn.config(fg=COLOR_P2)
            else:
                btn.config(fg="black")

    if game.round_over:
        return
    letter = game.get_current_letter()
    turn_label.config(
        text=(f"Player's turn - CURRENT LETTER: {letter}"
              if game.current_turn == "player"
              else f"AI's turn - CURRENT LETTER: {letter}")
    )


def disable_board():
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            buttons[r][c].config(state=tk.DISABLED)


def enable_board():
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            buttons[r][c].config(state=tk.NORMAL)


def _pass_results_text():
    return (f"Final Score\n\n"
            f"Player 1: {game.scores[0]}\n"
            f"Player 2: {game.scores[1]}\n")


def _solo_results_text():
    p, a = game.get_scores()
    pt, at = game.get_targets()
    return f"Final Score\n\nPlayer ({pt}): {p}\nAI ({at}): {a}\n"


# =========================================================
#  SCREEN SWITCHING
# =========================================================

def start_game(selected_mode):
    global game, game_mode, solo_round
    game_mode = selected_mode

    if selected_mode == "solo":
        game = GameAI()
        game.player_score = 0
        game.ai_score = 0
        solo_round = 1
        game.start_round()
    else:
        game = PatTapGame()

    menu_frame.pack_forget()
    tutorial_frame.pack_forget()
    results_frame.pack_forget()
    game_frame.pack(fill=tk.BOTH, expand=True)

    next_button.config(state=tk.DISABLED)
    enable_board()
    refresh_ui()


def back_to_menu():
    game_frame.pack_forget()
    tutorial_frame.pack_forget()
    results_frame.pack_forget()
    menu_frame.pack(fill=tk.BOTH, expand=True)


def show_tutorial():
    menu_frame.pack_forget()
    game_frame.pack_forget()
    results_frame.pack_forget()
    tutorial_frame.pack(fill=tk.BOTH, expand=True)
    tutorial_canvas.yview_moveto(0)


def close_tutorial():
    tutorial_frame.pack_forget()
    menu_frame.pack(fill=tk.BOTH, expand=True)


def show_results(score_text, winner):
    results_score_label.config(text=score_text)
    if winner == 0:
        wt = "Player 1 wins the match!"
    elif winner == 1:
        wt = "Player 2 wins the match!"
    elif winner == "player":
        wt = "Player wins the match!"
    elif winner == "ai":
        wt = "AI wins the match!"
    else:
        wt = "The match is a tie!"
    results_winner_label.config(text=wt)
    game_frame.pack_forget()
    results_frame.pack(fill=tk.BOTH, expand=True)


def try_again():
    start_game(game_mode)


# =========================================================
#  EVENT HANDLERS
# =========================================================

def on_click(row, column):
    if game is None:
        return
    if game_mode == "pass":
        on_click_pass(row, column)
    else:
        on_click_solo(row, column)


def on_click_pass(row, column):
    if game.round_over or game.game_over:
        return
    if not game.place_letter(row, column):
        return
    refresh_ui()


def on_click_solo(row, column):
    if game.current_turn != "player" or game.round_over:
        return
    if not game.place_player_letter(row, column):
        return
    refresh_ui()
    if check_solo_round_result():
        return
    window.after(500, ai_move)


def ai_move():
    if game.round_over or game.current_turn != "ai":
        return
    refresh_solo_ui()
    game.make_ai_move()
    refresh_ui()
    if check_solo_round_result():
        return
    refresh_solo_ui()


def check_solo_round_result():
    if not game.round_over:
        return False
    w = game.get_round_winner()
    turn_label.config(text={
        "player": "Player wins the round!",
        "ai": "AI wins the round!",
        "tie": "Round ended in a tie!",
    }.get(w, ""))
    refresh_ui()
    disable_board()
    if solo_round >= TOTAL_ROUNDS:
        next_button.config(state=tk.DISABLED)
        window.after(800, lambda: show_results(_solo_results_text(),
                                               game.get_match_winner()))
    else:
        next_button.config(state=tk.NORMAL)
    return True


def next_action():
    global solo_round
    if game is None:
        return
    if game_mode == "pass":
        if not (game.round_over and not game.game_over):
            return
        game.new_round()
    else:
        if not game.round_over or solo_round >= TOTAL_ROUNDS:
            return
        solo_round += 1
        game.start_round()
    enable_board()
    next_button.config(state=tk.DISABLED)
    refresh_ui()


# =========================================================
#  MOUSE WHEEL
# =========================================================

def _on_mousewheel(event):
    tutorial_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def _on_mousewheel_linux(event):
    if event.num == 4:
        tutorial_canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        tutorial_canvas.yview_scroll(1, "units")


# =========================================================
#  WINDOW
# =========================================================

window = tk.Tk()
window.title("PAT/TAP")
window.geometry("460x560")
window.resizable(False, False)

# ---------- MENU ----------
menu_frame = tk.Frame(window)
menu_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(menu_frame, text="PAT/TAP",
         font=("Arial", 44, "bold")).pack(pady=(70, 40))
tk.Button(menu_frame, text="Solo", font=("Arial", 18), width=14,
          command=lambda: start_game("solo")).pack(pady=8)
tk.Button(menu_frame, text="Pass & Play", font=("Arial", 18), width=14,
          command=lambda: start_game("pass")).pack(pady=8)
tk.Button(menu_frame, text="Tutorial", font=("Arial", 18), width=14,
          command=show_tutorial).pack(pady=8)


# ---------- TUTORIAL ----------
tutorial_frame = tk.Frame(window)

tutorial_canvas = tk.Canvas(tutorial_frame, highlightthickness=0)
tutorial_scrollbar = tk.Scrollbar(tutorial_frame, orient="vertical",
                                  command=tutorial_canvas.yview)
tutorial_canvas.configure(yscrollcommand=tutorial_scrollbar.set)
tutorial_scrollbar.pack(side="right", fill="y")
tutorial_canvas.pack(side="left", fill=tk.BOTH, expand=True)

tutorial_content = tk.Frame(tutorial_canvas)
tutorial_window_id = tutorial_canvas.create_window(
    (0, 0), window=tutorial_content, anchor="nw"
)


def _resize_tutorial_content(event):
    tutorial_canvas.itemconfig(tutorial_window_id, width=event.width)


def _update_scrollregion(event):
    tutorial_canvas.configure(scrollregion=tutorial_canvas.bbox("all"))


tutorial_content.bind("<Configure>", _update_scrollregion)
tutorial_canvas.bind("<Configure>", _resize_tutorial_content)
tutorial_canvas.bind_all("<MouseWheel>", _on_mousewheel)
tutorial_canvas.bind_all("<Button-4>", _on_mousewheel_linux)
tutorial_canvas.bind_all("<Button-5>", _on_mousewheel_linux)

# --- Tutorial content ---
tk.Label(tutorial_content, text="HOW TO PLAY",
         font=("Arial", 22, "bold")).pack(pady=(15, 5))
tk.Label(tutorial_content, text="1. Build one of these words in order:",
         font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 4))

words_frame = tk.Frame(tutorial_content)
words_frame.pack(pady=2)


def word_row(parent, letters, label_text):
    row = tk.Frame(parent)
    row.pack(pady=3)
    tk.Label(row, text=label_text, font=("Arial", 11, "bold"),
             width=12, anchor="w").pack(side="left")
    for i, ch in enumerate(letters):
        tk.Label(row, text=ch, font=("Arial", 18, "bold"),
                 width=3, height=1, relief="ridge", borderwidth=2,
                 bg="#f0f0f0").pack(side="left", padx=2)
        if i < len(letters) - 1:
            tk.Label(row, text="→", font=("Arial", 14)).pack(side="left", padx=1)


word_row(words_frame, "PAT", "Word A:")
word_row(words_frame, "TAP", "Word B:")

tk.Label(tutorial_content,
         text="The letters must appear in this exact order,\n"
              "read either left-to-right or top-to-bottom.",
         font=("Arial", 10, "italic"),
         fg="#555555").pack(pady=(2, 6))

tk.Label(tutorial_content, text="2. Letters drop into the grid in this cycle:",
         font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))

seq_frame = tk.Frame(tutorial_content)
seq_frame.pack(pady=4)


def letter_box(parent, letter):
    tk.Label(parent, text=letter, font=("Arial", 20, "bold"),
             width=3, height=1, relief="ridge", borderwidth=2,
             bg="#f0f0f0").pack(side="left", padx=4)


letter_box(seq_frame, "A")
tk.Label(seq_frame, text="→", font=("Arial", 16)).pack(side="left", padx=2)
letter_box(seq_frame, "P")
tk.Label(seq_frame, text="→", font=("Arial", 16)).pack(side="left", padx=2)
letter_box(seq_frame, "T")
tk.Label(seq_frame, text="→", font=("Arial", 16)).pack(side="left", padx=2)
letter_box(seq_frame, "A")
tk.Label(seq_frame, text="…", font=("Arial", 16)).pack(side="left", padx=2)

tk.Label(tutorial_content,
         text="Players take turns placing the next letter\n"
              "wherever they want on the board.",
         font=("Arial", 10, "italic"),
         fg="#555555").pack(pady=(2, 6))

tk.Label(tutorial_content, text="3. Example — PAT formed horizontally:",
         font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))

example_pat = tk.Frame(tutorial_content)
example_pat.pack(pady=4)
sample_pat = [
    ["P", "A", "T", ""],
    ["",  "",  "",  ""],
    ["",  "",  "",  ""],
    ["",  "",  "",  ""],
]
sample_pat_colors = [
    [COLOR_P1, COLOR_P2, COLOR_P1, "black"],
    ["black", "black", "black", "black"],
    ["black", "black", "black", "black"],
    ["black", "black", "black", "black"],
]
for r in range(4):
    for c in range(4):
        tk.Label(example_pat, text=sample_pat[r][c],
                 fg=sample_pat_colors[r][c], width=3, height=1,
                 font=("Arial", 16, "bold"), relief="ridge",
                 borderwidth=1, bg="#f0f0f0").grid(row=r, column=c)

tk.Label(tutorial_content, text="4. Example — TAP formed vertically:",
         font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))

example_tap = tk.Frame(tutorial_content)
example_tap.pack(pady=4)
sample_tap = [
    ["T", "",  "",  ""],
    ["A", "",  "",  ""],
    ["P", "",  "",  ""],
    ["",  "",  "",  ""],
]
sample_tap_colors = [
    [COLOR_P1, "black", "black", "black"],
    [COLOR_P2, "black", "black", "black"],
    [COLOR_P1, "black", "black", "black"],
    ["black", "black", "black", "black"],
]
for r in range(4):
    for c in range(4):
        tk.Label(example_tap, text=sample_tap[r][c],
                 fg=sample_tap_colors[r][c], width=3, height=1,
                 font=("Arial", 16, "bold"), relief="ridge",
                 borderwidth=1, bg="#f0f0f0").grid(row=r, column=c)

tk.Label(tutorial_content,
         text="Blue = Player 1    Red = Player 2",
         font=("Arial", 10, "italic"),
         fg="#555555").pack(pady=(2, 4))

tk.Label(tutorial_content, text="5. Scoring:",
         font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
tk.Label(tutorial_content,
         text=("The point goes to whoever placed the LAST (3rd)\n"
               "letter that completed the word.\n"
               "In the examples above, Player 1 placed the final letter."),
         font=("Arial", 10),
         fg="#333333").pack(pady=(0, 10))
tk.Button(tutorial_content, text="Back to Menu", font=("Arial", 14),
          command=close_tutorial).pack(pady=(4, 20))


# ---------- GAME SCREEN ----------
game_frame = tk.Frame(window)

round_label = tk.Label(game_frame, text="Round 1 / 3",
                       font=("Arial", 16, "bold"))
round_label.pack(pady=(10, 0))
score_label = tk.Label(game_frame, text="Player 1: 0     Player 2: 0",
                       font=("Arial", 13))
score_label.pack()
turn_label = tk.Label(game_frame,
                      text="Player 1's turn - CURRENT LETTER: A",
                      font=("Arial", 15), height=2)
turn_label.pack(pady=5)

board_frame = tk.Frame(game_frame)
board_frame.pack()

buttons = [[None] * 4 for _ in range(4)]
for row in range(4):
    for column in range(4):
        buttons[row][column] = tk.Button(
            board_frame, text="", font=("Arial", 18, "bold"),
            width=4, height=2,
            command=lambda r=row, c=column: on_click(r, c))
        buttons[row][column].grid(row=row, column=column)

bottom_bar = tk.Frame(game_frame)
bottom_bar.pack(side=tk.BOTTOM, pady=12)
next_button = tk.Button(bottom_bar, text="Next Round",
                        font=("Arial", 14), state=tk.DISABLED,
                        command=next_action)
next_button.pack(side=tk.LEFT, padx=6)
tk.Button(bottom_bar, text="Menu", font=("Arial", 14),
          command=back_to_menu).pack(side=tk.LEFT, padx=6)


# ---------- RESULTS SCREEN ----------
results_frame = tk.Frame(window)

tk.Label(results_frame, text="GAME OVER",
         font=("Arial", 32, "bold")).pack(pady=(80, 20))
results_winner_label = tk.Label(results_frame, text="",
                                font=("Arial", 20, "bold"))
results_winner_label.pack(pady=(0, 30))
results_score_label = tk.Label(results_frame, text="",
                               font=("Arial", 16), justify="center")
results_score_label.pack(pady=(0, 40))
tk.Button(results_frame, text="Try Again", font=("Arial", 16), width=14,
          command=try_again).pack(pady=8)
tk.Button(results_frame, text="Menu", font=("Arial", 16), width=14,
          command=back_to_menu).pack(pady=8)

window.mainloop()