
class Cell(object):
    def __init__(self, bomb):
        self.revealed = False
        self.marked = False
        self.bomb = bomb

    def is_revealed(self):
        return self.revealed

    def reveal(self):
        self.revealed = True

    def mark(self):
        self.marked = True

    def unmark(self):
        self.marked = False

    def is_marked(self):
        return self.marked

    def is_bomb(self):
        return self.bomb == 1
