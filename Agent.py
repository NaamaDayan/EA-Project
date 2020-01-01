class Agent(object):
    def __init__(self, n, m, bombs):
        self.location = (0, 0)
        self.board = Board(n, m, bombs)

    def move(self, direction):
        self.location += direction

    def reveal(self):
        self.board.reveal(self.location)

    def mark(self):
        self.board.mark(self.location)

    def unmark(self):
        self.board.unmark(self.location)

    def num_bombs(self):
        return self.board.num_bombs(self.location)

