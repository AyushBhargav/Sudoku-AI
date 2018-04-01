from utils import *
from copy import copy
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
left_diagonal_units = [rs + str(ord(rs) - ord('A') + 1) for rs in 'ABCDEFGHI']
right_diagonal_units = [rs + str(9 - ord(rs) + ord('A')) for rs in 'ABCDEFGHI']
diagonal_units= [left_diagonal_units, right_diagonal_units]
unitlist = row_units + column_units + square_units + diagonal_units

# TODO: Update the unit list to add the new diagonal units
unitlist = unitlist


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers
    """
    for unit in unitlist:
        twins = [(box1, box2) for box1 in unit for box2 in unit if box1 != box2 and len(values[box1]) == 2 
                                                and len(values[box2]) == 2 and values[box1] == values[box2]]
        for t1,t2 in twins:
            for box in unit:
                if box == t1 or box == t2:
                    continue
                for n in values[t1]:
                    values[box] = values[box].replace(n, "") 
    return values


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    for box, value in values.items():
        if len(value) > 1:
            continue
        n = value
        ps = peers[box]
        for p in ps:
            values[p] = values[p].replace(value, "")
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned
    """
    for unit in unitlist:
        for i in range(1,10):
            boxes = [box for box in unit if str(i) in values[box]]
            if len(boxes) == 1:
                values[boxes[0]] = str(i)
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    is_running = True
    while is_running:
        count = {box:len(value) for box,value in values.items()}
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        is_running = any([len(value) != count[box] for box, value in values.items()])
        if any([len(value) == 0 for value in values.values()]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False
    """
    values = reduce_puzzle(values)
    if values == False:
        return False
    if all([len(value) == 1 for value in values.values()]):
        return values
    n_value, box = min((len(value), box) for box, value in values.items() if len(value) > 1)
    for n in values[box]:
        new_values = values.copy()
        new_values[box] = n
        res = search(new_values)
        if res:
            return res 
    return False


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '2............................6..8...3...........6......4....8....................'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
