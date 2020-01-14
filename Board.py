import numpy as np
import random
from Cell import Cell

dicts = {0: '0️', 1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣'}


class Board(object):
    def __init__(self, n, m, bombs):
        self.n = n
        self.m = m
        self.grid = self.init_grid(n, m, bombs, 9999)
        self.bombs = bombs

    def reset(self, board_num):
        # for i in range(self.n):
        #     for j in range(self.m):
        #         self.grid_at((i, j)).reset()
        self.grid = self.init_grid(self.n, self.m, self.bombs, board_num)

    @staticmethod
    def init_grid(n, m, bombs, board_num):
        x = Board.random_grid(n, m, bombs, board_num)
        ret = []
        for i in range(n):
            row = []
            for j in range(m):
                row.append(Cell(x[i][j]))
            ret.append(row)
        return ret

    @staticmethod
    def random_grid(n, m, bombs, board_num):
        tmp = np.array([0] * (n * m - bombs) + [1] * bombs)
        random.Random(board_num).shuffle(tmp)
        return tmp.reshape((n, m))

    def reveal(self, loc):
        self.expand_cells(*loc)

    def expand_cells(self, row, column):
        cell = self.grid_at((row, column))
        cell.reveal()
        if self.num_bombs((row, column)) != 0:
            return
        for i in range(row - 1, row + 2):
            for j in range(column - 1, column + 2):
                if not self.in_grid(i, j) or i == row and j == column:  # i, j in board limits
                    continue
                neighbor = self.grid_at((i, j))
                if not (neighbor.is_marked() or neighbor.is_bomb() or neighbor.is_revealed()):
                    self.expand_cells(i, j)

    def in_grid(self, row, column):
        return 0 <= row < (len(self.grid)) and 0 <= column < (len(self.grid[0]))

    def mark(self, loc):
        self.grid_at(loc).mark()

    def unmark(self, loc):
        self.grid_at(loc).unmark()

    def num_helper(self, loc, pred):
        i, j = loc[0], loc[1]
        counter = 0
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if not self.in_grid(x, y):
                    continue
                if pred(self.grid_at((x, y))):
                    counter += 1
        return counter

    def num_bombs(self, loc):
        return self.num_helper(loc, lambda cell: cell.is_bomb())

    def num_unflagged_bombs(self, loc):
        return self.num_helper(loc, lambda cell: cell.is_bomb() and not cell.is_marked())

    def num_flags(self, loc):
        return self.num_helper(loc, lambda cell: cell.is_marked())

    def num_hidden(self, loc):
        return self.num_helper(loc, lambda cell: not cell.is_revealed() and not cell.is_marked())

    def apply_on_neighbors(self, loc, set_cell, max_sets):
        counter = 0
        i, j = loc[0], loc[1]
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if not self.in_grid(x, y) or counter > max_sets:
                    continue
                counter += 1
                set_cell((x, y))

    def flag_all(self, loc):
        self.apply_on_neighbors(loc, lambda x: self.mark(x), self.num_bombs(loc))

    def reveal_all(self, loc):
        self.apply_on_neighbors(loc, lambda x: self.reveal(x), 8 - self.num_bombs(loc))

    def grid_at(self, loc):
        return self.grid[loc[0]][loc[1]]

    # for fitness - returns true if a cell with a bomb was revealed
    def lost_game(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j].is_bomb() and self.grid[i][j].is_revealed():
                    return True
        return False

    # for fitness: returns number of clicked cells - number of bombs
    def num_revealed_cells(self):
        counter = 0
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                counter += int(self.grid[i][j].is_revealed() and not self.grid[i][j].is_bomb())
        return counter

    # for fitness - returns number of bombs that were correctly identified
    def num_correct_flags(self):
        correct_flags = 0
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                correct_flags += int(self.grid[i][j].is_bomb() and self.grid[i][j].is_marked())
        return correct_flags

    def print_board(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                print(int(self.grid[i][j].is_bomb()), end=" ")
            print()

    def print_revealed(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if not self.grid[i][j].is_revealed():
                    print("@", end=" ")
                else:
                    print(self.num_bombs((i, j)), end=" ")
            print()

    def finished(self):
        for i in range(self.n):
            for j in range(self.m):
                cell = self.grid_at((i, j))
                if not cell.is_bomb() and not cell.is_revealed():
                    return False
        return True

    def display(self):
        for i in range(self.n):
            for j in range(self.m):
                cell = self.grid_at((i, j))
                if cell.is_revealed():
                    char = '☪️' if cell.is_bomb() else dicts[self.num_bombs((i, j))]
                else:
                    char = '⏹️' if not cell.is_marked() else '✡️'
                print(char, end="")
            print()

    def display_debug(self):
        for i in range(self.n):
            for j in range(self.m):
                cell = self.grid_at((i, j))
                print('☪️' if cell.is_bomb() else dicts[self.num_bombs((i, j))], end="")
            print()
