"""
This file is a part of My-PyChess application.
In this file, we define the core chess-related functions.
For more understanding of the variables used here, checkout multiplayer.py
"""
from copy import deepcopy as copy

# This is a simple function that flips the side variable
# flip(0) returns 1 and flip(1) returns 0.
def flip(side):
    return int(not side)

# Return the type of piece given it's position
def getType(side, board, pos):
    for piece in board[side]:
        if piece[:2] == pos:
            return piece[2]

# Determine wether the position given is occupied by a piece of the given side.
def isOccupied(side, board, pos):
    for piece in board[side]:
        if piece[:2] == pos:
            return True
    return False

# Determine wether the position(s) given is(are) empty or not
def isEmpty(board, *poslist):
    for pos in poslist:
        for side in range(2):
            if isOccupied(side, board, pos):
                return False
    return True

# Determine if a specified square is attacked by enemy.
def isAttacked(side, board, pos):
    for piece in board[flip(side)]:
        x, y = piece[:2]
        if piece[2] == "p":
            if side and pos in [[x + 1, y - 1], [x - 1, y - 1]]:
                return True
            if not side and pos in [[x + 1, y + 1], [x - 1, y + 1]]:
                return True
        elif pos in availableMoves(side, board, piece, None):
            return True
    return False

# Determine wether the king is in check or not.
def isChecked(side, board):
    for piece in board[side]:
        if piece[2] == "k":
            return isAttacked(side, board, piece[:2])

# Determine all the possible LEGAL moves available for the side.
def legalMoves(side, board, flags):
    for piece in board[side]:
        for pos in availableMoves(side, board, piece, flags):
            if not isOccupied(side, board, pos):
                if moveTest(side, board, piece[:2], pos):
                    yield [piece[:2], pos]

# This function moves the piece from one coordinate to other.
# This function handles the capture of enemy, pawn promotion and en-passent.
# This does not check the validity of moves.
# One thing to note that this function directly modifies global value of the
# board variable from within the function, so pass a copy of the board
# variable if you do not want global modification of the board variable
def move(side, board, fro, to, promote="q"):
    UP = 8 if side else 1
    DOWN = 1 if side else 8
    allowENP = fro[1] == 4 + side and to[0] != fro[0] and isEmpty(board, to)
    for piece in board[flip(side)]:
        if piece[:2] == to:
            board[flip(side)].remove(piece)
            break

    for piece in board[side]:
        if piece[:2] == fro:
            piece[:2] = to
            if piece[2] == "k":
                if fro[0] - to[0] == 2:
                    move(side, board, [1, DOWN], [4, DOWN])
                elif to[0] - fro[0] == 2:
                    move(side, board, [8, DOWN], [6, DOWN])
                    
            if piece[2] == "p":
                if to[1] == UP:
                    board[side].remove(piece)
                    board[side].append([to[0], UP, promote])
                if allowENP:
                    board[flip(side)].remove([to[0], fro[1], "p"])
            break
    return board

# This function returns wether a move puts ones own king at check
def moveTest(side, board, fro, to):
    return not isChecked(side, move(side, copy(board), fro, to))

# This function returns wether a game has ended or not
def isEnd(side, board, flags):
    for _ in legalMoves(side, board, flags):
        return False
    return True

# This function returns wether a move is valid or not
def isValidMove(side, board, flags, fro, to):
    piece = fro + [getType(side, board, fro)]
    if not isOccupied(side, board, to):
        if to in availableMoves(side, board, piece, flags):
            return moveTest(side, board, fro, to)
    return False

# Does a routine check to update all the flags required for castling and
# enpassent. This function needs to be called AFTER every move played.
def updateFlags(side, board, fro, to, castle):
    if [5, 8, "k"] not in board[0] or [1, 8, "r"] not in board[0]:
        castle[0] = False
    if [5, 8, "k"] not in board[0] or [8, 8, "r"] not in board[0]:
        castle[1] = False
    if [5, 1, "k"] not in board[1] or [1, 1, "r"] not in board[1]:
        castle[2] = False
    if [5, 1, "k"] not in board[1] or [8, 1, "r"] not in board[1]:
        castle[3] = False

    enP = None
    if getType(side, board, to) == "p":
        if fro[1] - to[1] == 2:
            enP = [to[0], 6]
        elif to[1] - fro[1] == 2:
            enP = [to[0], 3]

    return (castle, enP)

# Given a side, board and piece, it returns all possible moves by the piese
# It does not validate wether the move is legal or not
def availableMoves(side, board, piece, flags):
    x, y, ptype = piece
    if ptype == "p":
        if not side:
            if y == 7 and isEmpty(board, [x, 6], [x, 5]):
                yield [x, 5]
            if isEmpty(board, [x, y - 1]):
                yield [x, y - 1]
                
            for i in ([x + 1, y - 1], [x - 1, y - 1]):
                if isOccupied(1, board, i) or flags[1] == i:
                    yield i
        else:
            if y == 2 and isEmpty(board, [x, 3], [x, 4]):
                yield [x, 4]
            if isEmpty(board, [x, y + 1]):
                yield [x, y + 1]

            for i in ([x + 1, y + 1], [x - 1, y + 1]):
                if isOccupied(0, board, i) or flags[1] == i:
                    yield i

    elif ptype == "n":
        for i, j in ((x + 1, y + 2), (x + 1, y - 2), (x - 1, y + 2),
                     (x - 1, y - 2), (x + 2, y + 1), (x + 2, y - 1),
                     (x - 2, y + 1), (x - 2, y - 1)):
            if i in range(1, 9) and j in range(1, 9):
                yield [i, j]

    elif ptype == "b":
        for i in range(1, 8):
            if x + i in range(1, 9) and y + i in range(1, 9):
                yield [x + i, y + i]
                if not isEmpty(board, [x + i, y + i]):
                    break
        for i in range(1, 8):
            if x + i in range(1, 9) and y - i in range(1, 9):
                yield [x + i, y - i]
                if not isEmpty(board, [x + i, y - i]):
                    break
        for i in range(1, 8):
            if x - i in range(1, 9) and y + i in range(1, 9):
                yield [x - i, y + i]
                if not isEmpty(board, [x - i, y + i]):
                    break
        for i in range(1, 8):
            if x - i in range(1, 9) and y - i in range(1, 9):
                yield [x - i, y - i]
                if not isEmpty(board, [x - i, y - i]):
                    break

    elif ptype == "r":
        for i in range(1, 8):
            if x + i in range(1, 9) and y in range(1, 9):
                yield [x + i, y]
                if not isEmpty(board, [x + i, y]):
                    break
        for i in range(1, 8):
            if x - i in range(1, 9) and y in range(1, 9):
                yield [x - i, y]
                if not isEmpty(board, [x - i, y]):
                    break
        for i in range(1, 8):
            if x in range(1, 9) and y + i in range(1, 9):
                yield [x, y + i]
                if not isEmpty(board, [x, y + i]):
                    break
        for i in range(1, 8):
            if x in range(1, 9) and y - i in range(1, 9):
                yield [x, y - i]
                if not isEmpty(board, [x, y - i]):
                    break

    elif ptype == "q":
        yield from availableMoves(side, board, [x, y, "b"], None)
        yield from availableMoves(side, board, [x, y, "r"], None)

    elif ptype == "k":
        if flags is not None and not isChecked(side, board):
            if flags[0][0] and isEmpty(board, [2, 8], [3, 8], [4, 8]):
                if not isAttacked(0, board, [4, 8]):
                    yield [3, 8]
            if flags[0][1] and isEmpty(board, [6, 8], [7, 8]):
                if not isAttacked(0, board, [6, 8]):
                    yield [7, 8]
            if flags[0][2] and isEmpty(board, [2, 1], [3, 1], [4, 1]):
                if not isAttacked(1, board, [4, 1]):
                    yield [3, 1]
            if flags[0][3] and isEmpty(board, [6, 1], [7, 1]):
                if not isAttacked(1, board, [6, 1]):
                    yield [7, 1]

        for i, j in ((x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x - 1, y),
                     (x - 1, y + 1), (x, y + 1), (x + 1, y + 1), (x + 1, y)):
            if i in range(1, 9) and j in range(1, 9):
                yield [i, j]