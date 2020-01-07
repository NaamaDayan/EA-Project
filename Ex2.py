import matplotlib.pyplot as plt
import operator
import random
import numpy as np
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

from Agent import Agent, Constants
from Functions import Functions


class Func(object):
    pass


class MyInt(object):
    pass


class GP(object):
    def __init__(self, n, m, bombs, gens, pop_size, num_problems, tree_max_height, crossover_p, mutate_p):
        self.n, self.m, self.bombs = n, m, bombs
        self.primitives = None
        self.toolbox = None
        self.gens = gens
        self.popSize = pop_size
        self.numProblems = num_problems
        self.treeMaxHeight = tree_max_height
        self.crossOverP = crossover_p
        self.mutateP = mutate_p
        self.agent = Agent(self.n, self.m, self.bombs)

    def init_vars(self):
        self.primitives = gp.PrimitiveSetTyped("MAIN", [], Func)

        # self.primitives.addPrimitive(Functions.if_then_else, [bool, Func, Func], Func)  # maybe 3
        # self.primitives.addPrimitive(Functions.eq, [int, int], bool)
        # self.primitives.addPrimitive(operator.and_, [bool, bool], bool)
        # self.primitives.addPrimitive(operator.or_, [bool, bool], bool)
        # self.primitives.addPrimitive(operator.gt, [int, int], bool)
        # self.primitives.addPrimitive(operator.lt, [int, int], bool)

        self.primitives.addPrimitive(Functions.prog2, [Func, Func], Func)
        self.primitives.addPrimitive(Functions.prog3, [Func, Func, Func], Func)

        # self.primitives.addPrimitive(self.agent.move, [MyInt], Func)

        # self.primitives.addPrimitive(Functions.id, [MyInt], MyInt)

        self.primitives.addPrimitive(Functions.if_all_safe(self.agent), [Func, Func], Func, "all_safe")
        self.primitives.addPrimitive(Functions.if_all_bombs(self.agent), [Func, Func], Func, "all_bombs")

        # self.primitives.addPrimitive(self.agent.num_bombs, [], int)
        # self.primitives.addPrimitive(self.agent.num_hidden, [], int)
        # self.primitives.addPrimitive(self.agent.num_flags, [], int)
        # self.primitives.addPrimitive(self.agent.num_unflagged_bombs, [], int)

        self.primitives.addTerminal(self.agent.mark, Func)
        self.primitives.addTerminal(self.agent.unmark, Func)
        self.primitives.addTerminal(self.agent.reveal, Func)
        self.primitives.addTerminal(self.agent.flag_all, Func)
        self.primitives.addTerminal(self.agent.uncover_all, Func)

        for key in Constants.directions:
            self.primitives.addTerminal(Functions.move(self.agent, key), Func,
                                        name="move{}".format(key))

        # self.primitives.addTerminal(False, bool)
        # self.primitives.addTerminal(True, bool)

        self.primitives.renameArguments(ARG0="agent")
        creator.create("FitnessMin", base.Fitness, weights=(1.0,))
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, pset=self.primitives)

        self.toolbox = base.Toolbox()
        self.toolbox.register("expr", gp.genHalfAndHalf, pset=self.primitives, min_=1, max_=2)
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.expr)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("compile", gp.compile, pset=self.primitives)

        self.toolbox.register("evaluate", self.eval_all_boards, problems=self.generate_problems(self.numProblems))
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("mate", gp.cxOnePointLeafBiased, 0.1)  # TODO maybe error
        self.toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
        self.toolbox.register("mutate", gp.mutUniform, expr=self.toolbox.expr_mut)  # , pset=self.primitives)

        self.toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
        self.toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

    def generate_problems(self, num):
        ret = []
        for _ in range(num):
            ret.append(Agent(self.n, self.m, self.bombs))
        return ret

    @staticmethod
    def eval_board(agent, actions, board_num):
        agent.run(actions, board_num)
        score = 2 * agent.board.num_revealed_cells()
        if agent.board.lost_game():
            score -= 1
        return score

    @staticmethod
    def max_fitness_for_board(board_game):
        return board_game.n * board_game.m - board_game.bombs

    def eval_all_boards(self, individual, problems):
        func = self.toolbox.compile(expr=individual, pset=self.primitives)
        # solutions_boards = [func(problem) for problem in problems]
        total_fitness = 0  # sum of all solutions' fitness
        max_fitness = 0
        non_dumbs = 0
        # print(individual)
        for i in range(self.numProblems):
            agent = self.agent
            curr_fitness = GP.eval_board(agent, func, i)
            total_fitness += curr_fitness
            if curr_fitness != 0:
                max_fitness += GP.max_fitness_for_board(agent.board)
            else:
                non_dumbs += 1
        std_score = max_fitness - total_fitness
        return 1 / (1 + std_score),

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

        ret_pop, ret_log = algorithms.eaSimple(pop, self.toolbox, self.crossOverP, self.mutateP, self.gens,
                                               stats=stats_fit,
                                               halloffame=hof, verbose=True)
        print(self.toolbox.compile(expr=hof[0])([1, 3, 2, 5, 4, 7, 6, 8]))
        return ret_pop, ret_log, hof


if __name__ == "__main__":
    board = (6, 6, 10)  # [N, M, k] NxM with k bombs
    # (gens, pop_size, num_problems, tree_max_height, crossover_p, mutate_p)
    # option_1 = (151, 50000, 36, 5, 0.9, 0.0)  # like paper
    option_1 = (100, 100, 3, 20, 0.9, 0.0)
    option_2 = (100, 1000, 100, 10, 0.7, 0.1)
    option_3 = (100, 100, 20, 10, 0.7, 0.1)
    option_4 = (100, 1000, 20, 10, 0.7, 0.01)
    options = [option_1, option_2, option_3, option_4]
    options = list(map(lambda x: board + x, options))
    for curr in [0]:  # range(len(options)):
        ex2 = GP(*options[curr])
        ex2.init_vars()
        ex2.fit()
        ex2.plot(curr)
    # board = Board(5, 2)
    # board.print_board()
    # board.expand_cells(3, 2)
    # print()
    # board.print_revealed()
