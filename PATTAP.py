from tkinter import *

# ---------- Screen switching ----------
def start_game(selected_mode):
    menu_frame.pack_forget()
    game_frame.pack(fill=BOTH, expand=True)


def back_to_menu():
    game_frame.pack_forget()
    menu_frame.pack(fill=BOTH, expand=True)


# ---------- Placeholder handlers ----------
def on_click(row, column):
    pass


def next_action():
    pass


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