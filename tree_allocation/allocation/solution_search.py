# Import modules
from tree_allocation.allocation.cpee_allocation import *
from tree_allocation.tree import R_RPST

# Import external packages
from lxml import etree
import numpy as np
import random
import time
from collections import defaultdict

class SolutionSearch():
    def __init__(self, process_allocation):
        self.solutions = []
        self.process_allocation = process_allocation
        self.process = process_allocation.process
        self.ns = {"cpee1" : list(self.process.nsmap.values())[0]}

class Genetic(SolutionSearch):
    def __init__(self, process_allocation, pop_size, generations,k_sel=3, k_mut=0.1):
        super(Genetic, self).__init__(process_allocation)
        self.pop_size = pop_size
        #TODO Genome = Process that is to be allocated/changed
        #self.genome_size = genome_size
        self.generations = generations
        self.k_mut = k_mut
        self.k_sel = k_sel
        self.best_tournament = [1000]
        
    def init_population(self, pop_size): #, genome_size): initialize the population of bit vectors
        #TODO create random solutions with number of pop_size
        population = []
        self.tasklist = self.process_allocation.process.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns)
        for pop in range(pop_size): 
            population.append({"branches" : self.build_individual()})
        return population

    def build_individual(self):
        # choose random branch per task:
        proc = copy.deepcopy(self.process)
        solution = Solution(proc)
        used_branches = {task:0 for task in self.tasklist}

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
        return used_branches
    
    def fitness(self, individual, measure):
        #TODO fitness = measure of the solution
        proc = copy.deepcopy(self.process)
        new_solution = Solution(proc)
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
    
    # tournament selection
    def selection(self, population, fitnesses):
        # keep the best solution
        # first random selection
        xo = False
        tournament = random.sample(range(len(population)-1), self.k_sel)
        tournament_fitnesses = [fitnesses[i] for i in tournament]
        winner_index = tournament[np.argmin(tournament_fitnesses)]
        for fitness in tournament_fitnesses:
            if fitness <= self.best_tournament[-1]:
                self.best_tournament.append(fitness)
                xo = True
                with open("xml7_out.xml", "wb") as f:
                    f.write(etree.tostring(self.evaluate_solution(population[winner_index]).process ))

                
        #[self.best_tournament.append(fitness) for fitness in tournament_fitnesses if fitness < self.best_tournament[-1]]
        return population[winner_index], xo
    
    def crossover(self, parent1, parent2): 
        #TODO Split the process and cross between the two parents
        # whats the best approach for handovers?
        proc_len = len(parent1["branches"].values())
        xo_point = random.randint(1, proc_len - 2)
        parent1_list = list(parent1["branches"].values())
        parent2_list = list(parent2["branches"].values())
        parent1_list, parent2_list = ([parent1_list[:xo_point] + parent2_list[xo_point:],
                parent2_list[:xo_point] + parent1_list[xo_point:]])
        
        parent1["branches"] = dict(zip(list(parent1["branches"].keys()), parent1_list))
        parent2["branches"] = dict(zip(list(parent2["branches"].keys()), parent2_list))
        return (parent1, parent2)
    
    def mutation(self, individual, k_mut = 0.1):
        #TODO change allocation randomly on one task
        for task, i in individual["branches"].items():
            b_range = len(self.process_allocation.allocations[task.attrib['id']].branches)-1
            if random.random() < k_mut and b_range > 0:
                while True:
                    no = random.randint(0, b_range)
                    if no != i:
                        break
                individual["branches"][task] = no
        return individual
    
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

    def evaluate_solution(self, individual):
        proc = copy.deepcopy(self.process)
        i=0

        new_solution = Solution(proc)
        new_solution.process = copy.deepcopy(self.process)
                # Find next task for solution

        tasks_iter = iter(self.tasklist)
        task = self.get_next_task(tasks_iter, new_solution)
        while True:
            allocation = self.process_allocation.allocations[task.attrib['id']]
            branch_no = individual["branches"].get(task)
            branch = allocation.branches[branch_no]
            #graphix.TreeGraph().show(etree.tostring(branch.node), filename="branch") 

            proc = branch.apply_to_process(proc, solution=new_solution)
            new_solution.process = proc
            task = self.get_next_task(tasks_iter, new_solution)
            if task == "end":
                break

        return new_solution
    
    def find_solutions(self, measure):
        #TODO change for process setting
        data = defaultdict(list)
        population = self.init_population(self.pop_size) #, self.genome_size) -> genome_size = size of process
        for gen in range(self.generations):

            start = time.time()
            fitnesses = [self.fitness(individual, measure) for individual in population]
            #print('Generation ', gen, '\n', list(zip(population, fitnesses)))
            nextgen_population = []
            for i in range(int(self.pop_size / 2)):
                parent1, xo1 = self.selection(population, fitnesses)  # select first parent
                parent2, xo2 = self.selection(population, fitnesses)  # select second parent

                offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
                # create new solutions and calculate measure
                nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)]
                #nextgen_population += [self.mutation(offspring1), self.mutation(offspring2)]  # mutate offspring
                a=1
            population = nextgen_population
            end = time.time()
            #print(f"Time for genereation: {end-start}")
            data["fitnesses"].append(fitnesses)
            data["avg_fit"].append(sum(fitnesses)/len(fitnesses))
            data["min_fit"].append(min(fitnesses))
            data["max_fit"].append(max(fitnesses))
        
        fin_pop = []
        for option in population:
            option["solution"] = self.evaluate_solution(option)
            fin_pop.append(option)
        
            with open("output.txt", "a") as f: 
            #{{'branches':list(option['branches'].values()), 'costs': list(option['solution'].get_measure(measure))} for option in population}
                string =str(list(option['branches'].values())) + "costs: " + str(option['solution'].get_measure(measure))
                f.write(string + "\n")

        return population, data
    
    def find_solutions_best_parents(self, measure):
        #TODO change for process setting
        data = defaultdict(list)
        population = self.init_population(self.pop_size) #, self.genome_size) -> genome_size = size of process
        for gen in range(self.generations):

            start = time.time()
            fitnesses = [self.fitness(individual, measure) for individual in population]
            #print('Generation ', gen, '\n', list(zip(population, fitnesses)))
            nextgen_population = []
            for i in range(int(self.pop_size / 2)):
                parent1, xo1 = self.selection(population, fitnesses)  # select first parent
                parent2, xo2 = self.selection(population, fitnesses)  # select second parent
                if xo1 or xo2:
                    nextgen_population +=  [parent1, parent2]

                else:
                    offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
                    # create new solutions and calculate measure
                    nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)]
                #nextgen_population += [self.mutation(offspring1), self.mutation(offspring2)]  # mutate offspring
                a=1
            population = nextgen_population
            data["fitnesses"].append(fitnesses)
            data["avg_fit"].append(sum(fitnesses)/len(fitnesses))
            data["min_fit"].append(min(fitnesses))
            data["max_fit"].append(max(fitnesses))
            

            end = time.time()
            #print(f"Time for genereation: {end-start}")
        
        fin_pop = []
        for option in population:
            option["solution"] = self.evaluate_solution(option)
            fin_pop.append(option)
        
            with open("output.txt", "a") as f: 
            #{{'branches':list(option['branches'].values()), 'costs': list(option['solution'].get_measure(measure))} for option in population}
                string =str(list(option['branches'].values())) + "costs: " + str(option['solution'].get_measure(measure))
                f.write(string + "\n")

        return population, data
    
    def find_solutions_random_insert_and_parent(self, measure):
        #TODO change for process setting
        data = defaultdict(list)
        population = self.init_population(self.pop_size) #, self.genome_size) -> genome_size = size of process
        for gen in range(self.generations):

            start = time.time()
            fitnesses = [self.fitness(individual, measure) for individual in population]
            #print('Generation ', gen, '\n', list(zip(population, fitnesses)))
            nextgen_population = []
            for i in range(int(self.pop_size / 2)-2):
                parent1, xo1 = self.selection(population, fitnesses)  # select first parent
                parent2, xo2 = self.selection(population, fitnesses)  # select second parent
                if xo1 or xo2:
                    nextgen_population +=  [parent1, parent2]

                else:
                    offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
                    # create new solutions and calculate measure
                    nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)]
                #nextgen_population += [self.mutation(offspring1), self.mutation(offspring2)]  # mutate offspring
                a=1
            nextgen_population += [{"branches" : self.build_individual(), "branches": self.build_individual()}]
            population = nextgen_population
            end = time.time()
            
            data["fitnesses"].append(fitnesses)
            data["avg_fit"].append(sum(fitnesses)/len(fitnesses))
            data["min_fit"].append(min(fitnesses))
            data["max_fit"].append(max(fitnesses))
            #print(f"Time for genereation: {end-start}")

        
        fin_pop = []
        for option in population:
            option["solution"] = self.evaluate_solution(option)
            fin_pop.append(option)
        
            with open("output.txt", "a") as f: 
            #{{'branches':list(option['branches'].values()), 'costs': list(option['solution'].get_measure(measure))} for option in population}
                string =str(list(option['branches'].values())) + "costs: " + str(option['solution'].get_measure(measure))
                f.write(string + "\n")

        return population, data
    
    def find_solutions_random_insert(self, measure):
        #TODO change for process setting
        data = defaultdict(list)
        population = self.init_population(self.pop_size) #, self.genome_size) -> genome_size = size of process
        for gen in range(self.generations):

            start = time.time()
            fitnesses = [self.fitness(individual, measure) for individual in population]
            #print('Generation ', gen, '\n', list(zip(population, fitnesses)))
            nextgen_population = []
            for i in range(int(self.pop_size / 2)-2):
                parent1, xo1 = self.selection(population, fitnesses)  # select first parent
                parent2, xo2 = self.selection(population, fitnesses)  # select second parent

                offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
                # create new solutions and calculate measure
                nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)]
                #nextgen_population += [self.mutation(offspring1), self.mutation(offspring2)]  # mutate offspring
                a=1
            nextgen_population += [{"branches" : self.build_individual(), "branches": self.build_individual()}]
            population = nextgen_population
            end = time.time()
            
            data["fitnesses"].append(fitnesses)
            data["avg_fit"].append(sum(fitnesses)/len(fitnesses))
            data["min_fit"].append(min(fitnesses))
            data["max_fit"].append(max(fitnesses))
            #print(f"Time for genereation: {end-start}")

        
        fin_pop = []
        for option in population:
            option["solution"] = self.evaluate_solution(option)
            fin_pop.append(option)
        
            with open("output.txt", "a") as f: 
            #{{'branches':list(option['branches'].values()), 'costs': list(option['solution'].get_measure(measure))} for option in population}
                string =str(list(option['branches'].values())) + "costs: " + str(option['solution'].get_measure(measure))
                f.write(string + "\n")

        return population, data

    def solver_factory(self, solve_type:str="plain", measure="cost"):
        localizer =  {
        "plain": self.find_solutions(measure),
        "random": self.find_solutions_random_insert(measure),
        "randomparent": self.find_solutions_random_insert_and_parent(measure),
        "parent": self.find_solutions_best_parents(measure)
        }
        return localizer[solve_type]


class Heuristic():
    pass

class Brute(SolutionSearch):
    def __init__(self, process_allocation):
        super(Brute, self).__init__(process_allocation)
    
    def find_solutions(self, tasks_iter=None, solution=None):
        #TODO should be callable with different options (Direct, Genetic, Heuristic, SemiHeuristic)
        """
        -> Add all Branches as new solutions
        -> for each branch, call, "new_solution(process, self, step+=1)"
        -> if i > 1: copy current solution and add new solution
        End: no further step
        """
        ns = {"cpee1" : list(self.process_allocation.process.nsmap.values())[0]}
        if not self.solutions: 
            
            tasklist = self.process_allocation.process.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=ns)
            self.solutions.append(Solution(copy.deepcopy(self.process_allocation.process)))
            return self.find_solutions(iter(tasklist), self.solutions[0])
        
        # Find next task for solution
        while True:
            task = next(tasks_iter, "end")
            if task == "end":
                print("Final Task reached. solution found")
                solution.check_validity()
                return
            
            # check that next task was not deleted:
            elif not solution.process.xpath(f"//*[@id='{task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=ns):
                pass
            
            else:
                break
        
        allocation = self.process_allocation.allocations[task.attrib['id']]
        test = allocation.branches[0].node
        with open("branch.xml", "wb") as f:
            f.write(etree.tostring(test))
        print("a")
        for i, branch in enumerate(allocation.branches):
            if i > 0:
                new_solution = copy.deepcopy(solution)
                self.solutions.append(new_solution)
            else: 
                solution_index=len(self.solutions)-1

        #TODO if less branches should be used: lower the amount of allocation.branches here
        for i, branch in enumerate(allocation.branches):
            #TODO Delete Solution if error in Change Operation
            if i > 0:
                solution = self.solutions[solution_index + i]
            #TODO ensure that label is the same too
            tasklabel = R_RPST.get_label(etree.tostring(task))
            task = solution.process.xpath(f"//*[@id='{task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=ns)[0]
            

            if branch.valid == False:
                solution.invalid_branches = True
            
            solution.process = branch.apply_to_process(solution.process, solution, task)
            open("xml_out3.xml", "wb").write(etree.tostring(solution.process))
            self.find_solutions(copy.deepcopy(tasks_iter), solution)
        
    def get_best_solutions(self, measure, operator=min, include_invalid=True, top_n=1):
        solutions_to_evaluate = self.solutions if include_invalid else filter(lambda x: x.invalid_branches == False, self.solutions)
        solution_measure = {solution: solution.get_measure(measure) for solution in solutions_to_evaluate}
        # Get the top N solutions
        sorted_solutions = sorted(solution_measure.items(), key=lambda x: x[1], reverse=(operator == max))
        top_solutions = [solution for solution, _ in sorted_solutions[:top_n]]

        return [{solution: solution.get_measure("cost")} for solution in top_solutions]

def solution_search_factory():
    pass