from functools import partial


class Functions(object):

    @staticmethod
    def if_then_else(input1, output1, output2):
        return output1() if input1() else output2()

    @staticmethod
    def progn(*args):
        for arg in args:
            if arg is not None:
                arg()

    @staticmethod
    def prog2(out1, out2):
        return partial(Functions.progn, out1, out2)

    @staticmethod
    def prog3(out1, out2, out3):
        return partial(Functions.progn, out1, out2, out3)

    @staticmethod
    def eq(x, y):
        return lambda: x == y

    @staticmethod
    def id(x):
        return x

    @staticmethod
    def if_all_safe(agent):
        return lambda out1, out2: partial(Functions.if_then_else, agent.if_all_safe, out1, out2)

    @staticmethod
    def if_all_bombs(agent):
        return lambda out1, out2: partial(Functions.if_then_else, agent.if_all_bombs, out1, out2)

    @staticmethod
    def move(agent, direction):
        return lambda: agent.move(direction)

    # @staticmethod
    # def move(agent, x, y):
    #     agent.move((x, y))
    #
    # @staticmethod
    # def mark(agent):
    #     agent.mark()
    #
    # @staticmethod
    # def unmark(agent):
    #     agent.unmark()
