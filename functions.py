import random

ROWS = 6
COLS = 7

def get_moves(board):
    return [c for c in range(COLS) if board[0][c] == 0]

def drop_piece(board, col, player):
    new_board = [row[:] for row in board]
    for r in range(ROWS - 1, -1, -1):
        if new_board[r][col] == 0:
            new_board[r][col] = player
            break
    return new_board

def is_terminal(board):
    return all(board[0][c] != 0 for c in range(COLS))

def count_fours(board, player):
    total = 0
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == player for i in range(4)):
                total += 1
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r+i][c] == player for i in range(4)):
                total += 1
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == player for i in range(4)):
                total += 1
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r-i][c+i] == player for i in range(4)):
                total += 1
    return total

def heurestic(board):
    ai_score = count_fours(board, 2)
    human_score = count_fours(board, 1)
    return ai_score - human_score

def print_board(board):
    for row in board:
        print(" ".join(str(num) for num in row))
    print()

# Prevent terminal version from running on import (during GUI execution)
if __name__ == "__main__":
    board = [
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
    ]

    print_board(board)

    while not is_terminal(board):
        # Human move
        player = 1
        plr = int(input("enter col to play: "))
        board = drop_piece(board, plr, player)
        print_board(board)

        # AI move
        player = 2
        ai = random.randint(0, COLS - 1)
        board = drop_piece(board, ai, player)
        print_board(board)
