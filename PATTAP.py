from tkinter import *
import random

# ---------- Settings (from the game spec) ----------
GRID = 4
ROUNDS = 3
WORDS = ["PAT", "TAP"]
SEQUENCES = {
    1: ["A", "T", "P"],   # Player 1 places A -> T -> P (cycling)
    2: ["P", "A", "T"],   # Player 2 places P -> A -> T (cycling)
}
HIGHLIGHT = "#ffd166"

# ---------- Game state ----------
mode = None                      # "solo" or "pass"
names = {1: "Player 1", 2: "Player 2"}
target = {1: "PAT", 2: "TAP"}    # each player's word, assigned at match start
scores = {1: 0, 2: 0}
placed = {1: 0, 2: 0}            # letters placed this round (drives the A/T/P order)
current = 1
round_no = 1
round_over = False
match_over = False


# ---------- Screen switching ----------
def start_game(selected_mode):
    global mode
    mode = selected_mode
    names[1] = "Player 1"
    names[2] = "Computer" if mode == "solo" else "Player 2"
    menu_frame.pack_forget()
    game_frame.pack(fill=BOTH, expand=True)
    new_match()


def back_to_menu():
    game_frame.pack_forget()
    menu_frame.pack(fill=BOTH, expand=True)


# ---------- Helpers ----------
def next_letter(player):
    return SEQUENCES[player][placed[player] % 3]


def find_lines():
    """Returns a list of (word, cells) for every PAT/TAP on the board.
    Rows read left-to-right, columns read top-to-bottom."""
    lines = []
    for r in range(GRID):
        for c in range(GRID - 2):
            cells = [(r, c + i) for i in range(3)]
            word = "".join(buttons[rr][cc]['text'] for rr, cc in cells)
            if word in WORDS:
                lines.append((word, cells))
    for c in range(GRID):
        for r in range(GRID - 2):
            cells = [(r + i, c) for i in range(3)]
            word = "".join(buttons[rr][cc]['text'] for rr, cc in cells)
            if word in WORDS:
                lines.append((word, cells))
    return lines


def board_full():
    return all(buttons[r][c]['text'] != "" for r in range(GRID) for c in range(GRID))


def update_scoreboard():
    score_label.config(
        text=f"{names[1]} ({target[1]}): {scores[1]}     "
             f"{names[2]} ({target[2]}): {scores[2]}")


def update_turn():
    round_label.config(text=f"Round {round_no} / {ROUNDS}")
    turn_label.config(text=f"{names[current]}'s turn - CURRENT LETTER: {next_letter(current)}")
    update_scoreboard()


# ---------- Match / round flow ----------
def new_match():
    global scores, round_no, match_over
    scores = {1: 0, 2: 0}
    round_no = 1
    match_over = False
    words = WORDS[:]
    random.shuffle(words)
    target[1], target[2] = words
    start_round()


def start_round():
    global placed, current, round_over
    placed = {1: 0, 2: 0}
    current = 1
    round_over = False
    for r in range(GRID):
        for c in range(GRID):
            buttons[r][c].config(text="", bg=default_bg)
    next_button.config(state=DISABLED, text="Next Round")
    update_turn()


def end_round(lines):
    """A word was formed (or the board filled). Whoever OWNS the word scores,
    no matter who placed the final letter."""
    global round_over, match_over
    round_over = True
    found = {word for word, _ in lines}

    for _, cells in lines:
        for r, c in cells:
            buttons[r][c].config(bg=HIGHLIGHT)

    winners = [p for p in (1, 2) if target[p] in found]
    for p in winners:
        scores[p] += 1

    if len(winners) == 2:
        msg = "Both words formed - both players score!"
    elif len(winners) == 1:
        p = winners[0]
        msg = f"{target[p]} formed - {names[p]} scores!"
    else:
        msg = "Board full - no word formed, no points."

    if round_no == ROUNDS:
        match_over = True
        if scores[1] > scores[2]:
            msg += f"\nMatch over: {names[1]} wins!"
        elif scores[2] > scores[1]:
            msg += f"\nMatch over: {names[2]} wins!"
        else:
            msg += "\nMatch over: it's a TIE!"
        next_button.config(state=NORMAL, text="New Match")
    else:
        next_button.config(state=NORMAL, text="Next Round")

    round_label.config(text=f"Round {round_no} / {ROUNDS} finished")
    turn_label.config(text=msg)
    update_scoreboard()


def next_action():
    global round_no
    if match_over:
        new_match()
    else:
        round_no += 1
        start_round()


# ---------- Turns ----------
def play(row, column):
    """Places the current player's next letter. Returns True if it worked."""
    global current
    if round_over or buttons[row][column]['text'] != "":
        return False

    buttons[row][column]['text'] = next_letter(current)
    placed[current] += 1

    lines = find_lines()
    if lines:
        end_round(lines)
    elif board_full():
        end_round([])
    else:
        current = 2 if current == 1 else 1
        update_turn()
    return True


def on_click(row, column):
    # In Solo mode Player 2 is the computer, so ignore clicks on its turn
    if mode == "solo" and current == 2:
        return
    if play(row, column) and mode == "solo" and not round_over:
        window.after(600, computer_move)


def computer_move():
    if mode != "solo" or current != 2 or round_over:
        return

    letter = next_letter(2)
    scoring, safe, risky = [], [], []
    for r in range(GRID):
        for c in range(GRID):
            if buttons[r][c]['text'] != "":
                continue
            # Try the move, see what it would form, then undo it
            buttons[r][c]['text'] = letter
            found = {w for w, _ in find_lines()}
            buttons[r][c]['text'] = ""
            if target[2] in found and target[1] not in found:
                scoring.append((r, c))      # completes the computer's word only
            elif target[1] in found:
                risky.append((r, c))        # would hand the player a point
            else:
                safe.append((r, c))

    choice = scoring or safe or risky
    play(*random.choice(choice))


# ---------- Window ----------
window = Tk()
window.title("PAT/TAP")
window.geometry("460x560")

# ---------- Intro / menu screen ----------
menu_frame = Frame(window)
menu_frame.pack(fill=BOTH, expand=True)

Label(menu_frame, text="PAT/TAP", font=("Arial", 44, "bold")).pack(pady=(90, 50))

Button(menu_frame, text="Solo", font=("Arial", 18), width=14,
       command=lambda: start_game("solo")).pack(pady=8)
Button(menu_frame, text="Pass & Play", font=("Arial", 18), width=14,
       command=lambda: start_game("pass")).pack(pady=8)

# ---------- Game screen (hidden until a mode is picked) ----------
game_frame = Frame(window)

round_label = Label(game_frame, text="", font=("Arial", 16, "bold"))
round_label.pack(pady=(10, 0))

score_label = Label(game_frame, text="", font=("Arial", 13))
score_label.pack()

turn_label = Label(game_frame, text="", font=("Arial", 15), height=2)
turn_label.pack(pady=5)

board_frame = Frame(game_frame)
board_frame.pack()

buttons = [[None] * GRID for _ in range(GRID)]
for row in range(GRID):
    for column in range(GRID):
        buttons[row][column] = Button(
            board_frame, text="", font=("Arial", 18, "bold"), width=4, height=2,
            command=lambda row=row, column=column: on_click(row, column))
        buttons[row][column].grid(row=row, column=column)

default_bg = buttons[0][0].cget("bg")

bottom_bar = Frame(game_frame)
bottom_bar.pack(side=BOTTOM, pady=12)

next_button = Button(bottom_bar, text="Next Round", font=("Arial", 14),
                     state=DISABLED, command=next_action)
next_button.pack(side=LEFT, padx=6)

Button(bottom_bar, text="Menu", font=("Arial", 14),
       command=back_to_menu).pack(side=LEFT, padx=6)

window.mainloop()