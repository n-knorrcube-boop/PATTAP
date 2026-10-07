from tkinter import *
from ai import GameAI


# ---------- GAME ----------
game = GameAI()

current_round = 1


# ---------- Screen switching ----------
def start_game(selected_mode):
    global current_round

    current_round = 1

    # Reset scores when starting a new game
    game.player_score = 0
    game.ai_score = 0

    # Start first round
    game.start_round()

    menu_frame.pack_forget()
    game_frame.pack(fill=BOTH, expand=True)

    # Update game display
    update_round()
    update_score()
    update_turn()
    update_board()

    next_button.config(state=DISABLED)


def back_to_menu():
    game_frame.pack_forget()
    menu_frame.pack(fill=BOTH, expand=True)


# ---------- Board display ----------
def update_board():

    board = game.get_board()

    for row in range(4):
        for column in range(4):

            buttons[row][column].config(
                text=board[row][column]
            )


# ---------- Round display ----------
def update_round():

    round_label.config(
        text=f"Round {current_round} / 3"
    )


# ---------- Score display ----------
def update_score():

    player_score, ai_score = game.get_scores()

    player_target, ai_target = game.get_targets()

    score_label.config(
        text=f"Player 1 ({player_target}): {player_score}"
             f"     AI ({ai_target}): {ai_score}"
    )


# ---------- Turn display ----------
def update_turn():

    if game.round_over:
        return

    letter = game.get_current_letter()

    if game.current_turn == "player":

        turn_label.config(
            text=f"Player 1's turn - CURRENT LETTER: {letter}"
        )

    else:

        turn_label.config(
            text=f"AI's turn - CURRENT LETTER: {letter}"
        )


# ---------- Disable board ----------
def disable_board():

    for row in range(4):
        for column in range(4):

            buttons[row][column].config(
                state=DISABLED
            )


# ---------- Enable board ----------
def enable_board():

    for row in range(4):
        for column in range(4):

            buttons[row][column].config(
                state=NORMAL
            )


# ---------- Check round result ----------
def check_round_result():

    if not game.round_over:
        return False

    winner = game.get_round_winner()

    if winner == "player":

        turn_label.config(
            text="Player 1 wins the round!"
        )

    elif winner == "ai":

        turn_label.config(
            text="AI wins the round!"
        )

    elif winner == "tie":

        turn_label.config(
            text="Round ended in a tie!"
        )

    update_board()
    update_score()

    disable_board()

    # ---------- Check Match ----------
    if current_round == 3:

        match_winner = game.get_match_winner()

        if match_winner == "player":

            turn_label.config(
                text="Player 1 wins the match!"
            )

        elif match_winner == "ai":

            turn_label.config(
                text="AI wins the match!"
            )

        else:

            turn_label.config(
                text="The match is a tie!"
            )

        next_button.config(
            state=DISABLED
        )

    else:

        next_button.config(
            state=NORMAL
        )

    return True


# ---------- Player board click ----------
def on_click(row, column):

    # Only allow clicking during Player 1's turn
    if game.current_turn != "player":
        return

    # Do nothing if round is already over
    if game.round_over:
        return

    # Try to place player's letter
    successful = game.place_player_letter(
        row,
        column
    )

    # Invalid move
    if not successful:
        return

    # Update board
    update_board()

    # Update score
    update_score()

    # Check if player ended the round
    if check_round_result():
        return

    # Update turn
    update_turn()

    # ---------- AI Turn ----------
    window.after(
        500,
        ai_move
    )


# ---------- AI move ----------
def ai_move():

    # Make sure the round is still active
    if game.round_over:
        return

    # Make sure it is actually the AI's turn
    if game.current_turn != "ai":
        return

    # Update turn label
    update_turn()

    # Make AI move
    move = game.make_ai_move()

    if move is None:
        return

    # Update board
    update_board()

    # Update score
    update_score()

    # Check round result
    if check_round_result():
        return

    # Return to Player 1
    update_turn()


# ---------- Next round ----------
def next_action():
    global current_round

    # Only allow up to 3 rounds
    if current_round >= 3:
        return

    current_round += 1

    # Start new round
    game.start_round()

    # Update display
    update_round()
    update_score()
    update_turn()
    update_board()

    # Enable board
    enable_board()

    # Disable Next Round
    next_button.config(
        state=DISABLED
    )


# ---------- WINDOW ----------
window = Tk()
window.title("PAT/TAP")
window.geometry("460x560")

# ---------- INTRO / MENU SCREEN ----------
menu_frame = Frame(window)
menu_frame.pack(fill=BOTH, expand=True)

Label(menu_frame, text="PAT/TAP", font=("Arial", 44, "bold")).pack(pady=(90, 50))

Button(menu_frame, text="Solo", font=("Arial", 18), width=14,
       command=lambda: start_game("solo")).pack(pady=8)
Button(menu_frame, text="Pass & Play", font=("Arial", 18), width=14,
       command=lambda: start_game("pass")).pack(pady=8)

# ---------- Game screen (hidden until a mode is picked) ----------
game_frame = Frame(window)

round_label = Label(game_frame, text="Round 1 / 3", font=("Arial", 16, "bold"))
round_label.pack(pady=(10, 0))

score_label = Label(game_frame, text="Player 1 (PAT): 0     Player 2 (TAP): 0", font=("Arial", 13))
score_label.pack()

turn_label = Label(game_frame, text="Player 1's turn - CURRENT LETTER: A", font=("Arial", 15), height=2)
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