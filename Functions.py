import inspect
import sys
from functools import partial
import random


class Functions(object):

    @staticmethod
    def if_then_else(input1, output1, output2):
        return output1() if input1() else output2()

    @staticmethod
    def if_then_else2(input1, output1, output2):
        return partial(Functions.if_then_else, lambda: input1, output1, output2)

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
    def and_(x, y):
        return lambda: x & y

    @staticmethod
    def or_(x, y):
        return lambda: x | y

    @staticmethod
    def gt(x, y):
        return lambda: x > y

    @staticmethod
    def lt(x, y):
        return lambda: x < y

    @staticmethod
    def ne(x, y):
        return lambda: x != y

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
    def move(agent):
        return lambda: agent.move()

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

    @staticmethod
    def generate_safe(pset, min_, max_, terminal_types, type_=None):
        if type_ is None:
            type_ = pset.ret
        expr = []
        height = random.randint(min_, max_)
        stack = [(0, type_)]
        while len(stack) != 0:
            depth, type_ = stack.pop()

            if type_ in terminal_types:
                try:
                    term = random.choice(pset.terminals[type_])
                except IndexError:
                    _, _, traceback = sys.exc_info()
                    raise IndexError("The gp.generate function tried to add "
                                     "a terminal of type '%s', but there is "
                                     "none available." % (type_,)).with_traceback(traceback)
                if inspect.isclass(term):
                    term = term()
                expr.append(term)
            else:
                try:
                    # Might not be respected if there is a type without terminal args
                    if height <= depth or (depth >= min_ and random.random() < pset.terminalRatio):
                        primitives_with_only_terminal_args = [p for p in pset.primitives[type_] if
                                                              all([arg in terminal_types for arg in p.args])]

                        if len(primitives_with_only_terminal_args) == 0:
                            prim = random.choice(pset.primitives[type_])
                        else:
                            prim = random.choice(primitives_with_only_terminal_args)
                    else:
                        prim = random.choice(pset.primitives[type_])
                except IndexError:
                    _, _, traceback = sys.exc_info()
                    raise IndexError("The gp.generate function tried to add "
                                     "a primitive of type '%s', but there is "
                                     "none available." % (type_,)).with_traceback(traceback)
                expr.append(prim)
                for arg in reversed(prim.args):
                    stack.append((depth + 1, arg))
        return expr
