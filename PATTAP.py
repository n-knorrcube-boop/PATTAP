from tkinter import *
import random


def next_turn(row, column):
    global player

    if buttons[row][column]['text'] == "" and check_winner() is False:
        buttons[row][column]['text'] = player

        result = check_winner()

        if result is False:
            player = players[0] if player == players[1] else players[1]
            label.config(text=(player + " turn"))
        elif result is True:
            label.config(text=(player + " WINS!"))
        elif result == "TIE":
            label.config(text=("TIE"))


def check_winner():
    # Check rows
    for row in range(3):
        if buttons[row][0]['text'] == buttons[row][1]['text'] == buttons[row][2]['text'] != "":
            return True

    # Check columns
    for column in range(3):
        if buttons[0][column]['text'] == buttons[1][column]['text'] == buttons[2][column]['text'] != "":
            return True

    # Check for tie (no empty spaces left)
    for row in range(3):
        for column in range(3):
            if buttons[row][column]['text'] == "":
                return False

    return "TIE"


def empty_space():
    pass


def new_game():
    pass


window = Tk()
window.title("PAT/TAP")
window.geometry("400x400")

players = ["P", "T"]
player = random.choice(players)
buttons = [[0, 0, 0],
           [0, 0, 0],
           [0, 0, 0]]

label = Label(text=player + " turn", font=("Arial", 25))
label.pack(side=TOP)

reset_button = Button(text="Restart", font=("Arial", 15), command=new_game)
reset_button.pack(side=BOTTOM)

frame = Frame(window)
frame.pack()

for row in range(3):
    for column in range(3):
        buttons[row][column] = Button(frame, text="", font=("Arial", 15), width=5, height=2,
                                      command=lambda row=row, column=column: next_turn(row, column))
        buttons[row][column].grid(row=row, column=column)

window.mainloop()