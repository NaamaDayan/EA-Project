# import inspect

from Board import Board


class Agent(object):
    def __init__(self, n, m, bombs):
        self.location = (0, 0)
        self.board = Board(n, m, bombs)

    def reset(self, board_num):
        self.location = (0, 0)
        self.board.reset(board_num)

    def move(self):
        loc = self.get_interesting_cells().get()[1] if not\
            self.get_interesting_cells().empty() else (0, 0)
        if self.board.in_grid(*loc):
            self.location = loc

    def reveal(self):
        self.board.reveal(self.location)

    def mark(self):
        self.board.mark(self.location)

    def unmark(self):
        self.board.unmark(self.location)

    def num_bombs(self):
        return self.board.adj_bombs(self.location)

    def num_flags(self):
        return self.board.adj_flags(self.location)

    def num_hidden(self):
        return self.board.adj_hidden(self.location)

    def num_unflagged_bombs(self):
        return self.board.adj_unflagged_bombs(self.location)

    def flag_all(self):
        self.board.flag_all(self.location)

    def uncover_all(self):
        self.board.uncover_all(self.location)

    def run(self, actions, board_num):
        self.reset(board_num)
        # while not self.board.finished():  # TODO change
        actions()

    def if_all_safe(self):
        return self.num_flags() == self.num_bombs()

    def if_all_bombs(self):
        return self.num_hidden() == self.num_unflagged_bombs()

    def get_interesting_cells(self):
        return self.board.interesting_cells

    def display(self):
        print("Agent at: ({},{}) With board of size {}x{} and {} bombs"
              .format(self.location[0], self.location[1], self.board.n, self.board.m, self.board.bombs))
        self.board.display()

    def display_debug(self):
        print("Agent at: ({},{}) With board of size {}x{} and {} bombs"
              .format(self.location[0], self.location[1], self.board.n, self.board.m, self.board.bombs))
        self.board.display_debug()

    # Rule 1: if num_hidden == num_unflagged_bombs then all hidden are bombs
    # Rule 2: if num_flags == num_bombs then all are safe
