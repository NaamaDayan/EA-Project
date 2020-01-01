from functools import partial

import matplotlib.pyplot as plt
import operator
import random
import numpy as np
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp


class Cell(object):
    def __init__(self, bomb):
        self.revealed = False
        self.marked = False
        self.bomb = bomb

    def reveal(self):
        self.revealed = True

    def mark(self):
        self.marked = True

    def unmark(self):
        self.marked = False

    def is_bomb(self):
        return self.bomb == 1


class Board(object):
    def __init__(self, n, bombs):
        self.n = n
        self.grid = self.init_grid(n, bombs)

    @staticmethod
    def init_grid(n, bombs):
        ratio = bombs * 1.0 / (n * n)
        x = np.random.choice([0, 1], size=(n, n), p=[1 - ratio, ratio])
        ret = []
        for i in range(n):
            row = []
            for j in range(n):
                row.append(Cell(x[i][j]))
            ret.append(row)
        return ret

    def reveal(self, i, j):
        # TODO
        self.grid[i][j].reveal()

    def mark(self, i, j):
        self.grid[i][j].mark()

    def unmark(self, i, j):
        self.grid[i][j].unmark()

    def num_bombs(self, i, j):
        counter = 0
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if not self.in_grid(x, y):
                    continue
                if self.grid[x][y].is_bomb():
                    counter += 1
        return counter

    def in_grid(self, x, y):
        if x < 0 or y < 0:
            return False
        if x >= self.n or y >= self.n:
            return False
        return True


class Agent(object):
    def __init__(self, n, bombs):
        self.location = (0, 0)
        self.board = Board(n, bombs)

    def move(self, direction):
        self.location += direction


class Constants(object):
    directions = {
        0: (0, -1),  # 'left': 0,
        1: (-1, -1),  # 'left_up': 1,
        2: (-1, 0),  # 'up': 2,
        3: (-1, 1),  # 'right_up': 3,
        4: (0, 1),  # 'right': 4,
        5: (1, 1),  # 'right_down': 5,
        6: (1, 0),  # 'down': 7,
        7: (1, -1)  # 'left_down': 8
    }


class GP(object):
    def __init__(self, gens, pop_size, num_problems, tree_max_height, cross_over_p, mutate_p):
        self.pset = None
        self.toolbox = None
        self.gens = gens
        self.popSize = pop_size
        self.numProblems = num_problems
        self.treeMaxHeight = tree_max_height
        self.crossOverP = cross_over_p
        self.mutateP = mutate_p

    @staticmethod
    def if_then_else(input1, output1, output2):
        return output1() if input1() else output2()

    @staticmethod
    def progn(*args):
        for arg in args:
            arg()

    @staticmethod
    def prog2(out1, out2):
        return partial(GP.progn, out1, out2)

    @staticmethod
    def prog3(out1, out2, out3):
        return partial(GP.progn, out1, out2, out3)

    def init_vars(self):
        self.pset = gp.PrimitiveSet("MAIN", 0)
        self.pset.addPrimitive(self.if_then_else, 2)
        self.pset.addPrimitive(self.prog2, 2)
        self.pset.addPrimitive(self.prog3, 3)
        for _, val in Constants.directions:
            self.pset.addTerminal(val, int)
        self.pset.renameArguments(ARG0="arr")

        creator.create("FitnessMin", base.Fitness, weights=(1.0,))
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        self.toolbox.register("expr", gp.genHalfAndHalf, pset=self.pset, min_=2, max_=self.treeMaxHeight)
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.expr)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("compile", gp.compile, pset=self.pset)

        self.toolbox.register("evaluate", self.evalSymbReg, problems=self.get_m_problems_n_queens(self.numProblems))
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("mate", gp.cxOnePoint)
        self.toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
        self.toolbox.register("mutate", gp.mutUniform, expr=self.toolbox.expr_mut, pset=self.pset)

        self.toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
        self.toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

    @staticmethod
    def eval_solution(solution):
        penalty = 0
        for i in range(len(solution)):
            for j in range(i + 1, len(solution)):
                if solution[i] == solution[j] or abs(i - j) == abs(solution[i] - solution[j]):
                    penalty += 1
        return 1 / (penalty + 1)  # divide by 0?

    def evalSymbReg(self, individual, problems):
        func = self.toolbox.compile(expr=individual)
        solutions = [func(problem) for problem in problems]
        return sum([self.eval_solution(sol) for sol in solutions]),

    def plot(self, name):
        gens = range(self.gens + 1)
        plt.plot(gens, self.log.select("best"), 'b',
                 gens, self.log.select("average"), 'r',
                 gens, self.log.select("median"), 'y',
                 gens, self.log.select("worst"), 'g')
        plt.legend(labels=['best', 'average', 'median', 'worst'])
        plt.xlabel("generation number")
        plt.ylabel("fitness score")
        plt.title("fitness score by generations")
        plt.savefig(name + '.png')
        plt.show()

    def fit(self):
        random.seed(318)

        pop = self.toolbox.population(n=self.popSize)
        hof = tools.HallOfFame(1)

        stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
        stats_fit.register("average", np.mean)
        stats_fit.register("median", np.median)
        stats_fit.register("worst", np.min)
        stats_fit.register("best", np.max)

        self.pop, self.log = algorithms.eaSimple(pop, self.toolbox, self.crossOverP, self.mutateP, self.gens,
                                                 stats=stats_fit,
                                                 halloffame=hof, verbose=True)

        print(self.toolbox.compile(expr=hof[0])([1, 3, 2, 5, 4, 7, 6, 8]))
        return self.pop, self.log, hof


if __name__ == "__main__":
    option_1 = (100, 1000, 100, 5, 0.7, 0.1)
    option_2 = (100, 1000, 100, 10, 0.7, 0.1)
    option_3 = (100, 100, 20, 10, 0.7, 0.1)
    option_4 = (100, 1000, 20, 10, 0.7, 0.01)
    options = [option_1, option_2, option_3, option_4]
    for curr in range(len(options)):
        ex2 = GP(*options[curr])
        ex2.init_vars()
        ex2.fit()
        ex2.plot(curr)
