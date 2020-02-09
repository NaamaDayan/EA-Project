import matplotlib.pyplot as plt
import operator
import random
import numpy as np
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

from Agent import Agent
from Functions import Functions


class Func(object):
    pass


class Move(object):
    pass


class MyInt(object):
    pass


class GP(object):
    def __init__(self, n, m, bombs, gens, pop_size, num_problems, crossover_p, mutate_p):
        self.n, self.m, self.bombs = n, m, bombs
        self.primitives = None
        self.toolbox = None
        self.gens = gens
        self.log = None
        self.popSize = pop_size
        self.numProblems = num_problems
        self.crossOverP = crossover_p
        self.mutateP = mutate_p
        self.agent = Agent(self.n, self.m, self.bombs)
        self.final_func = None

    def init_vars(self):

        self.primitives = gp.PrimitiveSetTyped("MAIN", [], Func)

        self.primitives.addPrimitive(Functions.prog2, [Move, Func], Func)
        self.primitives.addPrimitive(Functions.move(self.agent), [], Move, "movepri")

        self.primitives.addTerminal(self.agent.move, Move)

        self.primitives.addPrimitive(Functions.if_all_safe(self.agent), [Func, Func], Func, "all_safe")
        self.primitives.addPrimitive(Functions.if_all_bombs(self.agent), [Func, Func], Func, "all_bombs")
        self.primitives.addTerminal(self.agent.flag_all, Func)
        self.primitives.addTerminal(self.agent.reveal_all, Func)

        # self.primitives.addTerminal(self.agent.do_stuff, Func)

        # self.primitives.addPrimitive(Functions.if_then_else2, [bool, Func, Func], Func)  # maybe 3
        # self.primitives.addPrimitive(Functions.eq, [MyInt, MyInt], bool)
        # self.primitives.addPrimitive(Functions.ne, [MyInt, MyInt], bool)
        # self.primitives.addPrimitive(Functions.and_, [bool, bool], bool)
        # self.primitives.addPrimitive(Functions.or_, [bool, bool], bool)
        # self.primitives.addPrimitive(Functions.gt, [MyInt, MyInt], bool)
        # self.primitives.addPrimitive(Functions.lt, [MyInt, MyInt], bool)

        # self.primitives.addPrimitive(Functions.prog3, [Func, Func, Func], Func)

        # self.primitives.addPrimitive(self.agent.move, [MyInt], Func)
        # self.primitives.addPrimitive(Functions.id, [MyInt], MyInt)


        # self.primitives.addPrimitive(self.agent.num_bombs, [], MyInt)
        # self.primitives.addPrimitive(self.agent.num_hidden, [], MyInt)
        # self.primitives.addPrimitive(self.agent.num_flags, [], MyInt)
        # self.primitives.addPrimitive(self.agent.num_unflagged_bombs, [], MyInt)


        # self.primitives.addTerminal(self.agent.flag, Func)
        # self.primitives.addTerminal(self.agent.unflag, Func)
        # self.primitives.addTerminal(self.agent.reveal, Func)
        # self.primitives.addTerminal(self.)

        # for i in range(8):
        #     self.primitives.addTerminal(i, MyInt)
        #
        # self.primitives.addTerminal(False, bool)
        # self.primitives.addTerminal(True, bool)

        self.primitives.renameArguments(ARG0="agent")
        creator.create("FitnessMin", base.Fitness, weights=(1.0,))
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, pset=self.primitives)

        self.toolbox = base.Toolbox()
        # self.toolbox.register("expr", Functions.generate_safe, pset=self.primitives, min_=1, max_=10,
        #                       terminal_types=[MyInt, bool, Func])
        self.toolbox.register("expr", gp.genHalfAndHalf, pset=self.primitives, min_=1, max_=5)
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.expr)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("compile", gp.compile, pset=self.primitives)

        self.toolbox.register("evaluate", self.eval_all_boards)  # , problems=self.generate_problems(self.numProblems))
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("mate", gp.cxOnePoint)  # TODO maybe error
        self.toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
        self.toolbox.register("mutate", gp.mutUniform, expr=self.toolbox.expr_mut, pset=self.primitives)

        self.toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
        self.toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

    def generate_problems(self, num):
        ret = []
        for _ in range(num):
            ret.append(Agent(self.n, self.m, self.bombs))
        return ret

    @staticmethod
    def eval_board(agent, actions, board_num):
        # print(actions)
        agent.run(actions, board_num)
        score = agent.board.num_revealed_cells() - agent.first_reveal
        if agent.board.lost_game():
            score -= 1
        return score

    @staticmethod
    def max_fitness_for_board(board_game, first):
        return board_game.n * board_game.m - board_game.bombs - first

    def eval_all_boards(self, individual):
        func = self.toolbox.compile(expr=individual, pset=self.primitives)
        # solutions_boards = [func(problem) for problem in problems]
        total_fitness = 0  # sum of all solutions' fitness
        max_fitness = 0
        non_dumbs = 0
        # print(individual)
        for i in range(self.numProblems):
            agent = self.agent
            curr_fitness = GP.eval_board(agent, func, i)
            if curr_fitness != -1:  # not dummy
                max_fitness += GP.max_fitness_for_board(agent.board, agent.first_reveal)
                total_fitness += curr_fitness
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
        plt.savefig("{}.png".format(name))
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

        ret_pop, self.log = algorithms.eaSimple(pop, self.toolbox, self.crossOverP, self.mutateP, self.gens,
                                                stats=stats_fit,
                                                halloffame=hof, verbose=True)
        # print(self.toolbox.compile(expr=hof[0])([1, 3, 2, 5, 4, 7, 6, 8]))
        print(hof[0])
        ag = self.agent
        ag.reset(999)
        ag.display()
        self.final_func = self.toolbox.compile(expr=hof[0])
        ag.run(self.final_func, 999)
        ag.display()

        return ret_pop, self.log, hof


if __name__ == "__main__":
    board = (10, 10, 5)  # [N, M, k] NxM with k bombs
    # (gens, pop_size, num_problems, tree_max_height, crossover_p, mutate_p)
    # option_1 = (151, 50000, 36, 5, 0.9, 0.0)  # like paper
    option_1 = (100, 100, 10, 0.9, 0.0)
    option_2 = (100, 1000, 100, 0.7, 0.1)
    option_3 = (100, 100, 20, 0.7, 0.1)
    option_4 = (100, 1000, 20, 0.7, 0.01)
    options = [option_1, option_2, option_3, option_4]
    options = list(map(lambda x: board + x, options))
    for curr in [0]:  # range(len(options)):
        print(*options[curr])
        ex2 = GP(*options[curr])
        ex2.init_vars()
        ex2.fit()
        ex2.plot(curr)
    # board = Board(5, 2)
    # board.print_board()
    # board.expand_cells(3, 2)
    # print()
    # board.print_revealed()
