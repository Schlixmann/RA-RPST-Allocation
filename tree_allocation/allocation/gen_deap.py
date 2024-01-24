from deap import base, creator, tools
import random
import copy
from lxml import etree

from tree_allocation.allocation import solution


class DeapGen():
    def __init__(self, process_allocation):
        self.process_allocation = process_allocation
        self.process = process_allocation.process
        self.ns = {"cpee1" : list(self.process.nsmap.values())[0]}
        self.tasklist = self.process_allocation.process.xpath(
                 "(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns)

        creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
        creator.create("Individual", dict, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()
        toolbox.register("attr_dict", self.build_individual)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_dict, n=len(self.tasklist))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        
        ind1 = toolbox.individual()
        print(ind1)
        print(ind1.fitness.valid)
        toolbox.register("evaluate", self.fitness)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        
        pop = toolbox.population(n=300)
        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        CXPB, MUTPB = 0.5, 0.2
        fits = [ind.fitness.values[0] for ind in pop]

            # Variable keeping track of the number of generations
        g = 0

        # Begin the evolution
        while max(fits) < 100 and g < 1000:
            # A new generation
            g = g + 1
            print("-- Generation %i --" % g)

                # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

                # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB: 
                toolbox.mutate(mutant)
                del mutant.fitness.values
        
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring

                # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)


    def build_individual(self,):
            proc = copy.deepcopy(self.process)
            solution = solution.Solution(proc)
            used_branches = {task:0 for task in self.tasklist}
            self.tasklist = self.process_allocation.process.xpath(
                 "(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns)

            tasks_iter = iter(self.tasklist)
            task = self.get_next_task(tasks_iter, solution)
            while True:
                allocation = self.process_allocation.allocations[task.attrib['id']]
                branch_no = random.randint(0, len(allocation.branches)-1)
                used_branches[task] = branch_no
                branch = allocation.branches[branch_no]
                solution.process = branch.apply_to_process(proc, solution=solution)
                task = self.get_next_task(tasks_iter, solution)
                if task == "end":
                    break
            return("branches", used_branches)

    def get_next_task(self,tasks_iter, solution):
        
        while True:
            task = next(tasks_iter, "end")
            if task == "end":
                print("Final Task reached. solution found")
                solution.check_validity()
                return task
            
            # check that next task was not deleted:
            elif not solution.process.xpath(f"//*[@id='{task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns):
                pass
            
            else:
                break
        return task
    
    def fitness(self, individual, measure="cost"):
        #TODO fitness = measure of the solution
        proc = copy.deepcopy(self.process)
        new_solution = solution.Solution(proc)
        check = new_solution.get_measure(measure)
        branch_measure = []

        tasks_iter = iter(self.tasklist)
        task = self.get_next_task(tasks_iter, new_solution)
        while True:
            allocation = self.process_allocation.allocations[task.attrib['id']]
            branch_no = individual["branches"].get(task)
            branch = allocation.branches[branch_no]
            branch_measure.append(branch.get_measure("cost"))
            proc = branch.apply_to_process(proc, solution=new_solution)
            new_solution.process = proc
            task = self.get_next_task(tasks_iter, new_solution)
            if task == "end":
                break
            
        
        value = new_solution.get_measure(measure)

        return value



