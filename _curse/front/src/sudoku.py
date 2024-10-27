sudoku = [
    [None, 6, 2, 9, None, 5, 3, None, 8],
    [8, 1, 5, None, None, None, 6, 9, 4],
    [3, None, 9, 6, 8, None, 5, None, 2],
    [1, 5, None, None, None, 6, 2, 8, 9],
    [None, 9, 8, None, None, None, 1, 6, 3],
    [None, 2, None, 8, None, None, 4, 5, 7],
    [9, 3, None, None, None, 8, 7, 4, 5],
    [2, None, None, None, None, None, 8, 3, None],
    [5, 8, None, 4, 3, 7, 9, 2, None],
]
tree_roots = []

def sudoku_is_solved() -> bool:
    for i in range(9):
        if None in sudoku[i]:
            return False
        if len(set(sudoku[i])) < 9:
            return False
        if len(set([row[i] for row in sudoku])) < 9:
            return False

def get_current_square_filled_members(x, y) -> list[int]:
    square_top = (x % 3) * 3
    square_left = (y % 3) * 3
    members = []
    for i in range(square_top, square_top + 3):
        for j in range(square_left, square_left + 3):
            if sudoku[i][j] is not None:
                members.append(sudoku[i][j])
    return members


while not sudoku_is_solved(sudoku):
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] is not None:
                continue

            available_variants = set(range(1, 10)).difference(get_current_square_filled_members())
            if len(available_variants) == 1:
                
                    


# 00 10 20 30 40 50 60 70 80

# 01 11 21 31 41 51 61 71 81

# 02 12 22 32 42 52 62 72 82

# 03 13 23 33 43 53 63 73 83

# 04 14 24 34 44 54 64 74 84

# 05 15 25 35 45 55 65 75 85

# 06 16 26 36 46 56 66 76 86

# 07 17 27 37 47 57 67 77 87

# 08 18 28 38 48 58 68 78 88