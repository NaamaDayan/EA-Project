import matplotlib.pyplot as plt
import operator
import random
import numpy
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp


class GP:
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
    def mod_6_n(arr):
        return len(arr) % 6 != 2 and len(arr) % 6 != 3

    @staticmethod
    def mod_6_n_2(arr):
        return len(arr) % 6 == 2

    @staticmethod
    def sort_left_half(arr):
        return sorted(arr[:int(len(arr) / 2)]) + arr[int(len(arr) / 2):]

    @staticmethod
    def sort_right_half(arr):
        return arr[:int(len(arr) / 2)] + sorted(arr[int(len(arr) / 2):])

    @staticmethod
    def sort_even_odd(arr):
        return list(filter(lambda x: x % 2 == 0, arr)) + list(filter(lambda x: x % 2 == 1, arr))

    @staticmethod
    def swap_1_3(arr):
        place_1 = arr.index(1)
        place_3 = arr.index(3)
        arr[place_1], arr[place_3] = arr[place_3], arr[place_1]
        return arr

    @staticmethod
    def move_5_end(arr):
        return [x for x in arr if x != 5] + [5]

    @staticmethod
    def move_2_end_even(arr):
        new_arr = [2] + [n for n in arr if n != 2]
        left_half = new_arr[:int(len(arr) / 2)]
        return [n for n in left_half if n != 2] + [2] + new_arr[int(len(arr) / 2):]

    @staticmethod
    def move_1_3_end(arr):
        arr.remove(1)
        arr.remove(3)
        arr += [1, 3]
        return arr

    @staticmethod
    def if_then_else(input1, output1, output2):
        return output1 if input1 else output2

    @staticmethod
    def get_m_problems_n_queens(m):
        all_permutations = []
        n_range = range(6, 12)
        for n_queens in n_range:
            perms = [list(numpy.random.permutation(list(range(1, n_queens+1)))) for i in range(m)]
            all_permutations += perms
        return all_permutations

    def init_vars(self):
        self.pset = gp.PrimitiveSetTyped("MAIN", [list], list)
        self.pset.addPrimitive(self.if_then_else, [bool, list, list], list)
        self.pset.addPrimitive(self.sort_left_half, [list], list)
        self.pset.addPrimitive(self.sort_right_half, [list], list)
        self.pset.addPrimitive(self.sort_even_odd, [list], list)
        self.pset.addPrimitive(self.swap_1_3, [list], list)
        self.pset.addPrimitive(self.move_1_3_end, [list], list)
        self.pset.addPrimitive(self.move_2_end_even, [list], list)
        self.pset.addPrimitive(self.move_5_end, [list], list)
        self.pset.addPrimitive(self.mod_6_n, [list], bool)
        self.pset.addPrimitive(self.mod_6_n_2, [list], bool)
        self.pset.addTerminal(True, bool)
        self.pset.addTerminal(False, bool)
        self.pset.renameArguments(ARG0="arr")

        creator.create("FitnessMin", base.Fitness, weights=(1.0,))
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        self.toolbox.register("expr", gp.genHalfAndHalf, pset=self.pset, min_=2, max_= self.treeMaxHeight)
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
            for j in range(i+1, len(solution)):
                if solution[i] == solution[j] or abs(i - j) == abs(solution[i] - solution[j]):
                    penalty += 1
        return 1 / (penalty+1)   # divide by 0?

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
        plt.savefig(name+'.png')
        plt.show()

    def fit(self):
        random.seed(318)

        pop = self.toolbox.population(n=self.popSize)
        hof = tools.HallOfFame(1)

        stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
        stats_fit.register("average", numpy.mean)
        stats_fit.register("median", numpy.median)
        stats_fit.register("worst", numpy.min)
        stats_fit.register("best", numpy.max)

        self.pop, self.log = algorithms.eaSimple(pop, self.toolbox, self.crossOverP, self.mutateP, self.gens, stats=stats_fit,
                                       halloffame=hof, verbose=True)

        print(self.toolbox.compile(expr=hof[0])([1,3,2,5,4,7,6,8]))
        return self.pop, self.log, hof


if __name__ == "__main__":
    option_1 = (100, 1000, 100, 5, 0.7, 0.1)
    option_2 = (100, 1000, 100, 10, 0.7, 0.1)
    option_3 = (100, 100, 20, 10, 0.7, 0.1)
    option_4 = (100, 1000, 20, 10, 0.7, 0.01)
    options = [option_1, option_2, option_3, option_4]
    for i in range(len(options)):
        ex2 = GP(*options[i])
        ex2.init_vars()
        ex2.fit()
        ex2.plot(i)
