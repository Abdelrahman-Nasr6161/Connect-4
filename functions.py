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
    sequences = []

    # horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == player for i in range(4)):
                sequences.append([c, c+1, c+2, c+3])

    # vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == player for i in range(4)):
                sequences.append([c]*4)

    # diagonal \
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == player for i in range(4)):
                sequences.append([c, c+1, c+2, c+3])

    # diagonal /
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r-i][c+i] == player for i in range(4)):
                sequences.append([c, c+1, c+2, c+3])

    return sequences,len(sequences)

def count_threes(board, player):
    sequences = []

    # horizontal
    for r in range(ROWS):
        for c in range(COLS - 2):
            seq = [board[r][c+i] for i in range(3)]
            left_open = c == 0 or board[r][c-1] == 0
            right_open = c+3 == COLS or board[r][c+3] == 0
            if seq.count(player) == 3 and (left_open or right_open):
                sequences.append([c, c+1, c+2])

    # vertical
    for c in range(COLS):
        for r in range(ROWS - 2):
            seq = [board[r+i][c] for i in range(3)]
            top_open = r == 0 or board[r-1][c] == 0
            bottom_open = r+3 == ROWS or board[r+3][c] == 0
            if seq.count(player) == 3 and (top_open or bottom_open):
                sequences.append([c]*3)

    # diagonal \
    for r in range(ROWS - 2):
        for c in range(COLS - 2):
            seq = [board[r+i][c+i] for i in range(3)]
            top_left_open = r == 0 or c == 0 or board[r-1][c-1] == 0
            bottom_right_open = r+3 == ROWS or c+3 == COLS or board[r+3][c+3] == 0
            if seq.count(player) == 3 and (top_left_open or bottom_right_open):
                sequences.append([c, c+1, c+2])

    # diagonal /
    for r in range(2, ROWS):
        for c in range(COLS - 2):
            seq = [board[r-i][c+i] for i in range(3)]
            bottom_left_open = r+1 == ROWS or c == 0 or board[r+1][c-1] == 0
            top_right_open = r-3 < 0 or c+3 == COLS or board[r-3][c+3] == 0
            if seq.count(player) == 3 and (bottom_left_open or top_right_open):
                sequences.append([c, c+1, c+2])

    return sequences,len(sequences)


def count_twos(board, player):
    sequences = []

    # horizontal
    for r in range(ROWS):
        for c in range(COLS - 1):
            seq = [board[r][c+i] for i in range(2)]
            left_open = c == 0 or board[r][c-1] == 0
            right_open = c+2 == COLS or board[r][c+2] == 0
            if seq.count(player) == 2 and (left_open or right_open):
                sequences.append([c, c+1])

    # vertical
    for c in range(COLS):
        for r in range(ROWS - 1):
            seq = [board[r+i][c] for i in range(2)]
            top_open = r == 0 or board[r-1][c] == 0
            bottom_open = r+2 == ROWS or board[r+2][c] == 0
            if seq.count(player) == 2 and (top_open or bottom_open):
                sequences.append([c]*2)

    # diagonal \
    for r in range(ROWS - 1):
        for c in range(COLS - 1):
            seq = [board[r+i][c+i] for i in range(2)]
            top_left_open = r == 0 or c == 0 or board[r-1][c-1] == 0
            bottom_right_open = r+2 == ROWS or c+2 == COLS or board[r+2][c+2] == 0
            if seq.count(player) == 2 and (top_left_open or bottom_right_open):
                sequences.append([c, c+1])

    # diagonal /
    for r in range(1, ROWS):
        for c in range(COLS - 1):
            seq = [board[r-i][c+i] for i in range(2)]
            bottom_left_open = r+1 == ROWS or c == 0 or board[r+1][c-1] == 0
            top_right_open = r-2 < 0 or c+2 == COLS or board[r-2][c+2] == 0
            if seq.count(player) == 2 and (bottom_left_open or top_right_open):
                sequences.append([c, c+1])

    return sequences,len(sequences)
def heurestic(board):
    CENTER_COL = COLS // 2

    def center_bonus(seq_cols):
        avg_col = sum(seq_cols) / len(seq_cols)
        return 1.0 + (3 - abs(CENTER_COL - avg_col)) * 0.1

    def weighted_count(count_func, board, player, base_weight):
        sequences, _ = count_func(board, player)  # unpack sequences
        total = 0
        for seq_cols in sequences:
            total += base_weight * center_bonus(seq_cols)
        return total

    ai_score_4 = weighted_count(count_fours, board, 2, 1.0)
    human_score_4 = weighted_count(count_fours, board, 1, 1.0)
    ai_score_3 = weighted_count(count_threes, board, 2, 0.5)
    human_score_3 = weighted_count(count_threes, board, 1, 0.5)
    ai_score_2 = weighted_count(count_twos, board, 2, 0.25)
    human_score_2 = weighted_count(count_twos, board, 1, 0.25)

    ai_score = ai_score_2 + ai_score_3 + ai_score_4
    human_score = human_score_2 + human_score_3 + human_score_4

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
    print(len(board[0]))
    print_board(board)

    while not is_terminal(board):
        pass
    #     # Human move
    #     player = 1
    #     valid_moves = get_moves(board)
    #     plr = -1
    #     while plr not in valid_moves:
    #         plr = int(input(f"Enter col to play (valid: {valid_moves}): "))
    #     board = drop_piece(board, plr, player)
    #     print_board(board)
    #     if is_terminal(board):
    #         break
    #     # AI move
    #     player = 2
    #     print("AI is thinking")
    #     _,ai_move = minimax(board,5,True)
    #     board = drop_piece(board, ai_move, player)
    #     print_board(board)
    # print("Game Over")
    # print(f"Player 1 4-in-a-rows : {count_fours(board,1)}")
    # print(f"Player 2 4-in-a-rows : {count_fours(board,2)}")
