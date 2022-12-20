player, opponent = 'x', 'o'


def isMovesLeft(board):
    for i in range(3):
        for j in range(3):
            if (board[i][j] == '_'):
                return True
    return False


def evaluate(b):
    # Checking for Rows for X or O victory.
    for row in range(3):
        if (b[row][0] == b[row][1] and b[row][1] == b[row][2]):
            if (b[row][0] == player):
                return 10
            elif (b[row][0] == opponent):
                return -10
    # Checking for Columns for X or O victory.
    for col in range(3):
        if (b[0][col] == b[1][col] and b[1][col] == b[2][col]):
            if (b[0][col] == player):
                return 10
            elif (b[0][col] == opponent):
                return -10
    # Checking for Diagonals for X or O victory.
    if (b[0][0] == b[1][1] and b[1][1] == b[2][2]):
        if (b[0][0] == player):
            return 10
        elif (b[0][0] == opponent):
            return -10
    if (b[0][2] == b[1][1] and b[1][1] == b[2][0]):
        if (b[0][2] == player):
            return 10
        elif (b[0][2] == opponent):
            return -10
    return 0


def alphabeta(board, isMax, alpha, beta):
    score = evaluate(board)

    if (score == 10):
        return score
    if (score == -10):
        return score
    if (isMovesLeft(board) == False):
        return 0

    if (isMax):
        best = -1000
        for i in range(3):
            for j in range(3):
                if (board[i][j] == '_'):
                    board[i][j] = player
                    value = alphabeta(board, not isMax, alpha, beta)
                    best = max(best, value)
                    board[i][j] = '_'
        return best
    else:
        best = 1000
        for i in range(3):
            for j in range(3):
                if (board[i][j] == '_'):
                    board[i][j] = opponent
                    value = alphabeta(board, not isMax, alpha, beta)
                    best = min(best, value)
                    board[i][j] = '_'
        return best


def minimax(board, isMax):
    score = evaluate(board)

    if (score == 10):
        return score
    if (score == -10):
        return score
    if (isMovesLeft(board) == False):
        return 0

    if (isMax):
        best = -1000
        for i in range(3):
            for j in range(3):
                if (board[i][j] == '_'):
                    board[i][j] = player
                    best = max(best, minimax(board, not isMax))
                    board[i][j] = '_'
        return best
    else:
        best = 1000
        for i in range(3):
            for j in range(3):
                if (board[i][j] == '_'):
                    board[i][j] = opponent
                    best = min(best, minimax(board, not isMax))
                    board[i][j] = '_'
        return best


def findBestMove(board):
    bestVal = -1000
    bestMove = (-1, -1)
    for i in range(3):
        for j in range(3):
            if (board[i][j] == '_'):
                board[i][j] = player
                moveVal = minimax(board, False)
                board[i][j] = '_'
                if (moveVal > bestVal):
                    bestMove = (i, j)
                    bestVal = moveVal
    return bestMove


def display(board):
    for i in board:
        for j in i:
            print(j, end=" ")
        print()


board = [
        ['_', '_', '_'],
        ['_', '_', '_'],
        ['_', '_', '_']
]

# Computer Starts


def play():
    while True:
        print("Computer's Turn")
        i, j = findBestMove(board)
        board[i][j] = player
        display(board)
        if evaluate(board) == 10:
            print("Computer Wins")
            break
        if isMovesLeft(board) == False:
            print("Draw")
            break
        print("Your Turn")
        i, j = map(int, input().split())
        while (i < 0 or i > 2 or j < 0 or j > 2 or board[i][j] != '_'):
            print("Invalid Move")
            i, j = map(int, input().split())
        board[i][j] = opponent
        display(board)
        if evaluate(board) == -10:
            print("You Win")
            break
        if isMovesLeft(board) == False:
            print("Draw")
            break
play()