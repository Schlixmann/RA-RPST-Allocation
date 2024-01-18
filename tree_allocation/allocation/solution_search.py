# Import modules
from tree_allocation.allocation.cpee_allocation import *

# Import external packages
from lxml import etree
import numpy as np
import random

class SolutionSearch():
    pass

class Genetic():
    def __init__(self, pop_size, genome_size, generations):
        self.pop_size = pop_size
        #TODO Genome = Process that is to be allocated/changed
        self.genome_size = genome_size
        self.generations = generations

    def init_population(self, pop_size, genome_size):  # initialize the population of bit vectors
        #TODO create random solutions with number of pop_size
        #
        return [random.choices(range(2), k=genome_size) for _ in range(pop_size)]
    
    def fitness(self, individual):
        #TODO fitness = measure of the solution
        return sum(individual)
    
    # tournament selection
    def selection(self, population, fitnesses, k=3):
        # keep the best solution
        # first random selection
        tournament = random.sample(range(len(population)), k=3)
        tournament_fitnesses = [fitnesses[i] for i in tournament]
        winner_index = tournament[np.argmax(tournament_fitnesses)]
        return population[winner_index]
    
    def crossover(self, parent1, parent2): 
        #TODO Split the process and cross between the two parents
        # whats the best approach for handovers?
        xo_point = random.randint(1, len(parent1) - 1)
        return ([parent1[:xo_point] + parent2[xo_point:],
                 parent2[:xo_point] + parent1[xo_point:]])
    
    def mutation(self, individual):
        #TODO change allocation randomly on one task
        for i in range(len(individual)):
            if random.random() < 0.1:
                individual = individual[:i] + [1-individual[i]] + individual[i + 1:]
        return individual

    def find_solution(self, process_allocation):
        #TODO change for process setting
        population = self.init_population(self.pop_size, self.genome_size)
        for gen in range(self.generations):
            fitnesses = [self.fitness(individual) for individual in population]
            print('Generation ', gen, '\n', list(zip(population, fitnesses)))
            nextgen_population = []
            for i in range(int(self.pop_size / 2)):
                parent1 = self.selection(population, fitnesses)  # select first parent
                parent2 = self.selection(population, fitnesses)  # select second parent
                offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
                nextgen_population += [self.mutation(offspring1), self.mutation(offspring2)]  # mutate offspring
            population = nextgen_population
        
        return population

class Heuristic():
    pass

class Brute():
    pass
    """
    def find_solutions(process_allocation, solution=None, task=None):
        #TODO should be callable with different options (Direct, Genetic, Heuristic, SemiHeuristic)

        if solution is None: 
            first_task = self.process.xpath("//cpee1:call|//cpee1:manipulate", namespaces=self.ns)[0]
            path = etree.ElementTree(self.process).getpath(first_task)
            next_task = self.process.xpath(path)[0].xpath("(following::cpee1:call|following::cpee1:manipulate)[1]", namespaces=self.ns)
            first_allocation = self.allocations[first_task.attrib["id"]]
            solution = Solution(copy.deepcopy(self.process)) 
            self.solutions.append(solution)

            #next_tasks = [next_task for _ in range(len(first_allocation.branches))]
            return self.find_solutions(self.solutions[0], first_task)
        
        allocation = self.allocations[task.attrib['id']]
                
        for i, branch in enumerate(allocation.branches):
            if i > 0:
                new_solution = copy.deepcopy(solution)
                self.solutions.append(new_solution)
            else: 
                solution_index=len(self.solutions)-1

        #TODO if less branches should be used: lower the amount of allocation.branches here
        for i, branch in enumerate(allocation.branches):
            #TODO Delete Solution if error in Change Operation
            new_solution = self.solutions[solution_index + i]
            task = new_solution.process.xpath(f"//*[@id='{task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns)[0]
            next_tasks = task.xpath("(following::cpee1:call|following::cpee1:manipulate)[1]", namespaces=self.ns)
            next_task = next_tasks[0] if next_tasks else None
            if branch.valid == False:
                new_solution.invalid_branches = True
            process, next_task = self.apply_branch_to_process(branch.node, new_solution.process, new_solution, next_task)

            if next_task:
                # check if next task still exists if not, find new next task:
                if not new_solution.process.xpath(f"//*[@id='{next_task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns):
                    next_task = task.xpath("(following::cpee1:call|following::cpee1:manipulate)[1]", namespaces=self.ns)[0]
                self.find_solutions(new_solution, next_task)
            else:
                print("Final Task reached. solution found")
                new_solution.check_validity()
                #TODO IF invalid branches: Delete Solution or try to solve delete?
                # currently: Solution is kept and delete just was not necessary
"""

def solution_search_factory():
    pass