import tkinter as tk
import random

GRID_SIZE = 4
TOTAL_ROUNDS = 3
LETTER_SEQUENCE = ("A", "P", "T")


# =========================================================
#  GAME LOGIC — PASS & PLAY (2 humans)
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
            self.round_winner = owner
            self._maybe_end_match()
            return {
                "success": True, "letter": letter, "player": player,
                "word": word, "point_to": owner, "scores": self.scores[:],
                "round_over": True, "game_over": self.game_over,
                "winner": self.match_winner,
            }

        self.current_player = 1 - player

        if all(cell is not None for row in self.grid for cell in row):
            self.round_over = True
            self.round_winner = -1
            self._maybe_end_match()
            return {
                "success": True, "letter": letter, "player": player,
                "word": None, "point_to": None, "scores": self.scores[:],
                "round_over": True, "game_over": self.game_over,
                "winner": self.match_winner,
            }

        return {
            "success": True, "letter": letter, "player": player,
            "word": None, "point_to": None, "scores": self.scores[:],
            "round_over": False, "game_over": False, "winner": None,
        }

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
#  GAME LOGIC — SOLO (Player vs AI)
# =========================================================

class GameAI:
    def __init__(self):
        self.player_score = 0
        self.ai_score = 0
        self.grid = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.placed_by = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.sequence_index = 0
        self.current_turn = "player"
        self.round_over = False
        self.round_winner = None

    def start_round(self):
        self.grid = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.placed_by = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.sequence_index = 0
        self.current_turn = "player"
        self.round_over = False
        self.round_winner = None

    def get_board(self):
        return [row[:] for row in self.grid]

    def get_scores(self):
        return self.player_score, self.ai_score

    def get_targets(self):
        return "PAT", "TAP"

    def get_current_letter(self):
        return LETTER_SEQUENCE[self.sequence_index % len(LETTER_SEQUENCE)]

    def get_round_winner(self):
        return self.round_winner

    def get_match_winner(self):
        if self.player_score > self.ai_score:
            return "player"
        if self.ai_score > self.player_score:
            return "ai"
        return "tie"

    def _place(self, row, col, owner):
        letter = self.get_current_letter()
        self.grid[row][col] = letter
        self.placed_by[row][col] = owner
        self.sequence_index += 1

        result = self.check_winner()
        if result:
            _, winner_owner = result
            self.round_over = True
            self.round_winner = winner_owner
            if winner_owner == "player":
                self.player_score += 1
            else:
                self.ai_score += 1
        elif all(cell is not None for r in self.grid for cell in r):
            self.round_over = True
            self.round_winner = "tie"

    def place_player_letter(self, row, col):
        if self.round_over or self.current_turn != "player":
            return False
        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return False
        if self.grid[row][col] is not None:
            return False

        self._place(row, col, "player")
        if not self.round_over:
            self.current_turn = "ai"
        return True

    def make_ai_move(self):
        if self.round_over or self.current_turn != "ai":
            return None

        move = self._choose_ai_move()
        if move is None:
            self.round_over = True
            self.round_winner = "tie"
            return None

        row, col = move
        self._place(row, col, "ai")
        if not self.round_over:
            self.current_turn = "player"
        return move

    def _empty_cells(self):
        return [(r, c)
                for r in range(GRID_SIZE)
                for c in range(GRID_SIZE)
                if self.grid[r][c] is None]

    def _choose_ai_move(self):
        empties = self._empty_cells()
        if not empties:
            return None

        current = self.get_current_letter()

        for (r, c) in empties:
            if self._would_complete(r, c, current, "ai"):
                return (r, c)

        for (r, c) in empties:
            if self._would_complete(r, c, current, "player"):
                return (r, c)

        best = None
        best_score = -1
        for (r, c) in empties:
            score = self._position_value(r, c, current)
            if score > best_score:
                best_score = score
                best = (r, c)
        if best is not None and best_score > 0:
            return best

        return random.choice(empties)

    def _would_complete(self, row, col, letter, owner):
        self.grid[row][col] = letter
        self.placed_by[row][col] = owner
        result = self.check_winner()
        self.grid[row][col] = None
        self.placed_by[row][col] = None
        return result is not None

    def _position_value(self, row, col, letter):
        value = 0
        for dr, dc in ((0, 1), (1, 0)):
            for start in (-2, -1, 0):
                cells = [(row + dr * (start + k), col + dc * (start + k))
                         for k in range(3)]
                if any(not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE)
                       for r, c in cells):
                    continue
                seq = []
                for (r, c) in cells:
                    if (r, c) == (row, col):
                        seq.append(letter)
                    else:
                        v = self.grid[r][c]
                        seq.append(v if v is not None else "?")
                if self._could_match(seq):
                    value += 1
        return value

    @staticmethod
    def _could_match(seq):
        for target in ("PAT", "TAP"):
            if all(s == "?" or s == t for s, t in zip(seq, target)):
                return True
        return False

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
#  STATE
# =========================================================

game = None
game_mode = None
solo_round = 1


# =========================================================
#  UI HELPERS
# =========================================================

def refresh_ui():
    if game is None:
        return
    if game_mode == "pass":
        refresh_pass_ui()
    else:
        refresh_solo_ui()


def refresh_pass_ui():
    round_label.config(text=f"Round {game.round_number} / {TOTAL_ROUNDS}")
    score_label.config(
        text=f"Player 1: {game.scores[0]}     Player 2: {game.scores[1]}"
    )

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            letter = game.grid[r][c]
            owner = game.placed_by[r][c]
            btn = buttons[r][c]
            btn.config(text=letter or "")
            btn.config(state=tk.NORMAL)
            if owner == 0:
                btn.config(fg="#1f6feb")
            elif owner == 1:
                btn.config(fg="#d7263d")
            else:
                btn.config(fg="black")

    if game.round_over:
        if game.round_winner == 0:
            turn_label.config(text="Player 1 wins the round!")
        elif game.round_winner == 1:
            turn_label.config(text="Player 2 wins the round!")
        else:
            turn_label.config(text="Round ended in a tie!")

        disable_board()

        if game.game_over:
            next_button.config(state=tk.DISABLED)
            window.after(800, lambda: show_results(
                _pass_results_text(),
                game.match_winner
            ))
        else:
            next_button.config(state=tk.NORMAL)
    else:
        turn = game.current_player + 1
        turn_label.config(
            text=f"Player {turn}'s turn - CURRENT LETTER: "
                 f"{game.get_next_letter()}"
        )


def refresh_solo_ui():
    round_label.config(text=f"Round {solo_round} / {TOTAL_ROUNDS}")

    player_score, ai_score = game.get_scores()
    player_target, ai_target = game.get_targets()
    score_label.config(
        text=f"Player ({player_target}): {player_score}"
             f"     AI ({ai_target}): {ai_score}"
    )

    board = game.get_board()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            letter = board[r][c]
            owner = game.placed_by[r][c]
            btn = buttons[r][c]
            btn.config(text=letter or "")
            if owner == "player":
                btn.config(fg="#1f6feb")
            elif owner == "ai":
                btn.config(fg="#d7263d")
            else:
                btn.config(fg="black")

    if game.round_over:
        return

    letter = game.get_current_letter()
    if game.current_turn == "player":
        turn_label.config(text=f"Player's turn - CURRENT LETTER: {letter}")
    else:
        turn_label.config(text=f"AI's turn - CURRENT LETTER: {letter}")


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
    return (f"Final Score\n\n"
            f"Player: {p}\n"
            f"AI: {a}\n")


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
    results_frame.pack_forget()
    game_frame.pack(fill=tk.BOTH, expand=True)

    next_button.config(state=tk.DISABLED)
    enable_board()
    refresh_ui()


def back_to_menu():
    game_frame.pack_forget()
    results_frame.pack_forget()
    menu_frame.pack(fill=tk.BOTH, expand=True)


def show_tutorial():
    # Placeholder — tutorial removed
    pass


def show_results(score_text, winner):
    results_score_label.config(text=score_text)

    if winner == 0:
        winner_text = "Player 1 wins the match!"
    elif winner == 1:
        winner_text = "Player 2 wins the match!"
    elif winner == "player":
        winner_text = "Player wins the match!"
    elif winner == "ai":
        winner_text = "AI wins the match!"
    else:
        winner_text = "The match is a tie!"

    results_winner_label.config(text=winner_text)

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

    result = game.place_letter(row, column)
    if not result["success"]:
        return

    refresh_ui()


def on_click_solo(row, column):
    if game.current_turn != "player":
        return
    if game.round_over:
        return

    if not game.place_player_letter(row, column):
        return

    refresh_ui()

    if check_solo_round_result():
        return

    window.after(500, ai_move)


def ai_move():
    if game.round_over:
        return
    if game.current_turn != "ai":
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

    winner = game.get_round_winner()
    if winner == "player":
        turn_label.config(text="Player wins the round!")
    elif winner == "ai":
        turn_label.config(text="AI wins the round!")
    else:
        turn_label.config(text="Round ended in a tie!")

    refresh_ui()
    disable_board()

    if solo_round >= TOTAL_ROUNDS:
        next_button.config(state=tk.DISABLED)
        window.after(800, lambda: show_results(
            _solo_results_text(),
            game.get_match_winner()
        ))
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
        enable_board()
        refresh_ui()
    else:
        if not game.round_over:
            return
        if solo_round >= TOTAL_ROUNDS:
            return
        solo_round += 1
        game.start_round()
        enable_board()
        next_button.config(state=tk.DISABLED)
        refresh_ui()


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

tk.Label(menu_frame, text="PAT/TAP", font=("Arial", 44, "bold")).pack(pady=(70, 40))

tk.Button(menu_frame, text="Solo", font=("Arial", 18), width=14,
          command=lambda: start_game("solo")).pack(pady=8)
tk.Button(menu_frame, text="Pass & Play", font=("Arial", 18), width=14,
          command=lambda: start_game("pass")).pack(pady=8)
tk.Button(menu_frame, text="Tutorial", font=("Arial", 18), width=14,
          command=show_tutorial).pack(pady=8)


# ---------- GAME SCREEN ----------
game_frame = tk.Frame(window)

round_label = tk.Label(game_frame, text="Round 1 / 3", font=("Arial", 16, "bold"))
round_label.pack(pady=(10, 0))

score_label = tk.Label(game_frame, text="Player 1: 0     Player 2: 0",
                       font=("Arial", 13))
score_label.pack()

turn_label = tk.Label(game_frame, text="Player 1's turn - CURRENT LETTER: A",
                      font=("Arial", 15), height=2)
turn_label.pack(pady=5)

board_frame = tk.Frame(game_frame)
board_frame.pack()

buttons = [[None] * 4 for _ in range(4)]
for row in range(4):
    for column in range(4):
        buttons[row][column] = tk.Button(
            board_frame, text="", font=("Arial", 18, "bold"), width=4, height=2,
            command=lambda r=row, c=column: on_click(r, c))
        buttons[row][column].grid(row=row, column=column)

bottom_bar = tk.Frame(game_frame)
bottom_bar.pack(side=tk.BOTTOM, pady=12)

next_button = tk.Button(bottom_bar, text="Next Round", font=("Arial", 14),
                        state=tk.DISABLED, command=next_action)
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