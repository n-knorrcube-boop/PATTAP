import random


# ---------- GAME AI ----------
class GameAI:

    def __init__(self):
        # ---------- BOARD ----------
        self.board = [
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""]
        ]

        # ---------- LETTER SEQUENCES ----------
        self.player_sequence = ["A", "T", "P"]
        self.ai_sequence = ["P", "A", "T"]

        self.player_letter_index = 0
        self.ai_letter_index = 0

        # ---------- SCORES ----------
        self.player_score = 0
        self.ai_score = 0

        # ---------- TARGET WORDS ----------
        self.player_target = ""
        self.ai_target = ""

        # ---------- GAME STATE ----------
        self.current_turn = "player"
        self.round_over = False
        self.round_winner = None

    # ---------- START ROUND ----------
    def start_round(self):
        self.board = [
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""]
        ]

        self.player_letter_index = 0
        self.ai_letter_index = 0

        self.current_turn = "player"
        self.round_over = False
        self.round_winner = None

        # Randomly assign PAT and TAP
        if random.choice([True, False]):
            self.player_target = "PAT"
            self.ai_target = "TAP"
        else:
            self.player_target = "TAP"
            self.ai_target = "PAT"

    # ---------- GET PLAYER LETTER ----------
    def get_player_letter(self):
        return self.player_sequence[
            self.player_letter_index
        ]

    # ---------- GET AI LETTER ----------
    def get_ai_letter(self):
        return self.ai_sequence[
            self.ai_letter_index
        ]

    # ---------- GET CURRENT LETTER ----------
    def get_current_letter(self):
        if self.current_turn == "player":
            return self.get_player_letter()

        return self.get_ai_letter()

    # ---------- GET EMPTY CELLS ----------
    def get_empty_cells(self):
        empty_cells = []

        for row in range(4):
            for column in range(4):

                if self.board[row][column] == "":
                    empty_cells.append((row, column))

        return empty_cells

    # ---------- VALIDATE MOVE ----------
    def is_valid_move(self, row, column):

        if row < 0 or row >= 4:
            return False

        if column < 0 or column >= 4:
            return False

        if self.board[row][column] != "":
            return False

        return True

    # ---------- PLAYER MOVE ----------
    def place_player_letter(self, row, column):

        if self.current_turn != "player":
            return False

        if self.round_over:
            return False

        if not self.is_valid_move(row, column):
            return False

        letter = self.get_player_letter()

        self.board[row][column] = letter

        self.player_letter_index = (
            self.player_letter_index + 1
        ) % len(self.player_sequence)

        # Check if a target word was completed
        winner = self.check_winner()

        if winner is not None:
            self.round_winner = winner
            self.round_over = True
            self.add_score(winner)

            return True

        # Check if board is full
        if self.is_board_full():
            self.round_over = True
            self.round_winner = "tie"

            return True

        # Give turn to AI
        self.current_turn = "ai"

        return True

    # ---------- CHECK WORD ----------
    def check_word(self, target_word):

        # ---------- HORIZONTAL ----------
        for row in range(4):

            for column in range(2):

                word = (
                    self.board[row][column]
                    + self.board[row][column + 1]
                    + self.board[row][column + 2]
                )

                if word == target_word:
                    return True

        # ---------- VERTICAL ----------
        for row in range(2):

            for column in range(4):

                word = (
                    self.board[row][column]
                    + self.board[row + 1][column]
                    + self.board[row + 2][column]
                )

                if word == target_word:
                    return True

        return False

    # ---------- CHECK WINNER ----------
    def check_winner(self):

        # Player owns whichever target word was assigned to them
        if self.check_word(self.player_target):
            return "player"

        # AI owns whichever target word was assigned to it
        if self.check_word(self.ai_target):
            return "ai"

        return None

    # ---------- CHECK BOARD FULL ----------
    def is_board_full(self):
        return len(self.get_empty_cells()) == 0

    # ---------- CHOOSE AI MOVE ----------
    def choose_ai_move(self):

        empty_cells = self.get_empty_cells()

        if not empty_cells:
            return None

        ai_letter = self.get_ai_letter()

        # ---------- TRY TO WIN ----------
        winning_moves = []

        for row, column in empty_cells:

            self.board[row][column] = ai_letter

            if self.check_word(self.ai_target):
                winning_moves.append((row, column))

            self.board[row][column] = ""

        if winning_moves:
            return random.choice(winning_moves)

        # ---------- TRY TO AVOID PLAYER WIN ----------
        safe_moves = []

        for row, column in empty_cells:

            self.board[row][column] = ai_letter

            player_wins = self.check_word(
                self.player_target
            )

            self.board[row][column] = ""

            if not player_wins:
                safe_moves.append((row, column))

        if safe_moves:
            return random.choice(safe_moves)

        # ---------- RANDOM MOVE ----------
        return random.choice(empty_cells)

    # ---------- AI MOVE ----------
    def make_ai_move(self):

        if self.current_turn != "ai":
            return None

        if self.round_over:
            return None

        if self.is_board_full():
            return None

        move = self.choose_ai_move()

        if move is None:
            return None

        row, column = move

        letter = self.get_ai_letter()

        self.board[row][column] = letter

        self.ai_letter_index = (
            self.ai_letter_index + 1
        ) % len(self.ai_sequence)

        # Check if AI or player target was completed
        winner = self.check_winner()

        if winner is not None:
            self.round_winner = winner
            self.round_over = True
            self.add_score(winner)

        elif self.is_board_full():
            self.round_over = True
            self.round_winner = "tie"

        else:
            self.current_turn = "player"

        return row, column

    # ---------- GET BOARD ----------
    def get_board(self):
        return self.board

    # ---------- GET SCORES ----------
    def get_scores(self):
        return self.player_score, self.ai_score

    # ---------- GET TARGETS ----------
    def get_targets(self):
        return self.player_target, self.ai_target

    # ---------- GET ROUND WINNER ----------
    def get_round_winner(self):
        return self.round_winner

    # ---------- ADD SCORE ----------
    def add_score(self, winner):

        if winner == "player":
            self.player_score += 1

        elif winner == "ai":
            self.ai_score += 1

    # ---------- GET MATCH WINNER ----------
    def get_match_winner(self):

        if self.player_score > self.ai_score:
            return "player"

        if self.ai_score > self.player_score:
            return "ai"

        return "tie"