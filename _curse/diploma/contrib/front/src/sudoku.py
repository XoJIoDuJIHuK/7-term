class Node:
    def __init__(
        self,
        parent = None,
        children: list = None,
        value: int = None,
        position: list[tuple[int, int]] = None
    ):
        self.parent = parent
        self.children = [] if children is None else children
        self.value = value
        self.position = position

hard_sudoku = [
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
hard_sudoku_v2 = [
    [None, None, None, 5, None, None, None, None, None],
    [6, None, None, None, 8, 1, None, 2, None],
    [None, 8, 1, None, 6, None, 3, 9, 5],
    [None, 3, None, None, None, None, 9, 1, None],
    [None, None, None, 8, None, 7, None, None, None],
    [None, 1, 6, None, None, None, None, 4, None],
    [8, 7, 4, None, 2, None, 1, 5, None],
    [None, 9, None, 4, 5, None, None, None, 8],
    [None, None, None, None, None, 8, None, None, None],
]
easy_sudoku = [
    [None, None, 9, 3, None, 4, None, 5, None],
    [3, None, 8, 9, 5, None, 7, None, None],
    [None, 4, None, None, None, None, None, 9, 1],
    [4, None, None, 8, None, 2, None, 3, 5],
    [None, 8, None, None, 4, None, None, 2, None],
    [9, 5, None, 7, None, 6, None, None, 4],
    [2, 9, None, None, None, None, None, 1, None],
    [None, None, 7, None, 1, 9, 8, None, 2],
    [None, 1, None, 6, None, 3, 5, None, None],
]

sudoku = hard_sudoku_v2
root = Node()
current_node = root
changed = True
rejected_possibilities = []


def print_sudoku():
    for i in range(9):
        print(sudoku[i])


def get_possibility_tuple(x: int, y: int, value: int) -> tuple[int, int, int]:
    return (x, y, value)



def sudoku_is_solved() -> bool:
    for i in range(9):
        if None in sudoku[i]:
            return False
        row = set(sudoku[i])
        if len(row) < 9:
            return False
        column = set([row[i] for row in sudoku])
        if len(column) < 9:
            return False
    return True

def get_current_square_filled_members(
    square_top_left_x: int,
    square_top_left_y: int,
) -> list[int]:
    members = []
    for i in range(square_top_left_x, square_top_left_x + 3):
        for j in range(square_top_left_y, square_top_left_y + 3):
            if sudoku[i][j] is not None:
                members.append(sudoku[i][j])
    return members


def get_possible_positions(
    value: int,
    positions: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    if len(positions) == 0:
        raise Exception(f'length of positions is 0. value: {value}')
    square_top_left_x = (positions[0][0] % 3) * 3
    square_top_left_y = (positions[0][1] % 3) * 3
    available_positions = []
    for position in positions:
        x_in_square = position[0] - square_top_left_x
        y_in_square = position[1] - square_top_left_y
        if (
            value not in sudoku[position[0]] and
            value not in [sudoku[i][position[1]] for i in range(9)]
        ):
            available_positions.append(position)
    return available_positions


def get_current_square_available_members(
    square_top_left_x: int,
    square_top_left_y: int
) -> list[int]:
    return list(set(range(1, 10)).difference(get_current_square_filled_members(
        square_top_left_x,
        square_top_left_y
    )))


def get_free_slots(
    square_top_left_x: int,
    square_top_left_y: int
) -> list[tuple[int, int]]:
    slots = []
    for i in range(square_top_left_x, square_top_left_x + 3):
        for j in range(square_top_left_y, square_top_left_y + 3):
            if sudoku[i][j] is None:
                slots.append((i, j))
    return slots


while not sudoku_is_solved():
    current_possibilities = {}
    if not changed:
        if len(current_node.children) > 0:
            current_node = current_node.children[0]
            new_x = current_node.position[0]
            new_y = current_node.position[1]
            new_value = current_node.value
            if sudoku[new_x][new_y] is not None:
                print_sudoku()
                raise Exception(f'Position is taken: ({new_x}:{new_y})')
            sudoku[new_x][new_y] = new_value
        else:
            current_x = current_node.position[0]
            current_y = current_node.position[1]
            current_value = current_node.value
            if current_node is root:
                print_sudoku()
                raise Exception('infinite loop')
            rejected_possibilities.append(get_possibility_tuple(
                x=current_x, y=current_y, value=current_value
            ))
            sudoku[current_x][current_y] = None
            current_node = current_node.parent
            current_node.children = current_node.children[1:]

    changed = False
    try:
        for vertical_square_index in range(3):
            for horizontal_square_index in range(3):
                available_members = get_current_square_available_members(
                    vertical_square_index * 3,
                    horizontal_square_index * 3
                )
                for value in available_members:
                    available_positions = get_possible_positions(
                        value,
                        get_free_slots(
                            vertical_square_index * 3,
                            horizontal_square_index * 3
                        )
                    )
                    if len(available_positions) == 0:
                        print_sudoku()
                        raise Exception(f'Value {value} has 0 possible positions. Square number: [{vertical_square_index}:{horizontal_square_index}]')
                    if len(available_positions) == 1:
                        position = available_positions[0]
                        sudoku[position[0]][position[1]] = value
                        changed = True
                    else:
                        index_tuple = (vertical_square_index, horizontal_square_index, value)
                        current_possibilities[index_tuple] = available_positions
        def filter_possibilities(element) -> bool:
            for position in element[1]:
                if get_possibility_tuple(position[0], position[1], element[0][2]) in rejected_possibilities:
                    return False
            return True

        current_possibilities = list(filter(
            filter_possibilities,
            current_possibilities.items()
        ))
        if not changed and len(current_possibilities) > 0:
            sorted_possibilities = sorted(
                current_possibilities,
                key=lambda x: len(x[1])
            )
            possibility_object = sorted_possibilities[0]
            for position in possibility_object[1]:
                current_node.children.append(Node(
                parent=current_node,
                children=None,
                value=possibility_object[0][2],
                position=position
            ))
            # TODO: change ^^^
    except Exception as e:
        print(e)
        changed = False


print_sudoku()