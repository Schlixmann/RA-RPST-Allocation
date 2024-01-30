# Import modules
from tree_allocation.allocation.cpee_allocation import *
from tree_allocation.allocation.solution import Solution
from tree_allocation.tree import R_RPST
from tree_allocation.allocation.utils import get_next_task

# Import external packages
from lxml import etree
import numpy as np
import random
import time
from collections import defaultdict
import os
import pickle
import uuid
import itertools
from itertools import repeat
from tqdm import tqdm
import multiprocessing as mp

class SolutionSearch():

    def __init__(self, process_allocation):
        self.solutions = []
        self.process_allocation = process_allocation
        self.process = process_allocation.process
        self.ns = {"cpee1" : list(self.process.nsmap.values())[0]}

class Genetic(SolutionSearch):

    def __init__(self, process_allocation, pop_size, generations, k_sel=3, k_mut=0.1, early_abandon=True):
        super(Genetic, self).__init__(process_allocation)
        self.pop_size:int = pop_size
        #TODO Genome = Process that is to be allocated/changed
        #self.genome_size = genome_size
        self.generations:int = generations
        self.k_mut:float = k_mut
        self.k_sel:int = k_sel
        self.best_tournament = [1000]
        self.best_tournament_str:str = []
        self.early_abandon:bool=early_abandon
        
    def init_population(self, pop_size): #, genome_size): initialize the population of bit vectors
        # create random solutions for number of pop_size

        population = []
        self.tasklist = self.process_allocation.process.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns)
        for pop in range(pop_size): 
            population.append({"branches" : self.build_individual()})
        return population

    def build_individual(self):
        # choose random branch per task:

        solution = Solution(copy.deepcopy(self.process))
        used_branches = {task:0 for task in self.tasklist}
        tasks_iter = iter(self.tasklist)
        task = get_next_task(tasks_iter, solution)
        while True:
            allocation = self.process_allocation.allocations[task.attrib['id']]
            branch_no = random.randint(0, len(allocation.branches)-1)
            used_branches[task] = branch_no
            #branch = allocation.branches[branch_no]
            #solution.process = branch.apply_to_process(solution.process, solution=solution)
            task = get_next_task(tasks_iter, solution)
            if task == "end":
                break
        
        return used_branches
    
    def fitness(self, individual, measure:str="cost", rtype:str = "value"):
        # calculate the fitness of a solution

        new_solution = Solution(copy.deepcopy(self.process)) # create solution
        tasks_iter = iter(self.tasklist) # iterator
        task = get_next_task(tasks_iter, new_solution) # gets next tasks and checks for deletes

        while True:
            allocation = self.process_allocation.allocations[task.attrib['id']] # get allocatin

            branch_no = individual["branches"].get(task)    # get choosen number of branch
            branch = allocation.branches[branch_no] # get actual branch as R-RPST

            new_solution.process = branch.apply_to_process(new_solution.process, solution=new_solution) # build branch
            
            task = get_next_task(tasks_iter, new_solution)
            if task == "end":
                break
        
        new_solution.check_validity()
        if new_solution.invalid_branches:
            value = np.nan        
        else:
            value = new_solution.get_measure(measure)   # calc. fitness of solution

        if rtype=="solution":
            return new_solution
        else:
            return value
    
    # tournament selection
    def selection(self, population, fitnesses, gen):
        
        xo = False # init xo flag
        tournament = random.sample(range(len(population)-1), self.k_sel)
        tournament_fitnesses = [fitnesses[i] for i in tournament]
        winner_index = tournament[np.argmin(tournament_fitnesses)]
 
        if fitnesses[winner_index] <= self.best_tournament[-1]:

            self.best_tournament.append(fitnesses[winner_index])
            xo = True # flag to keep as elitist parent

        return copy.copy(population[winner_index]), xo
    
    # parent crossover
    def crossover(self, parent1, parent2): 
        parent1, parent2 = (copy.copy(parent1), copy.copy(parent2))

        proc_len = len(parent1["branches"].values())
        xo_point = random.randint(1, proc_len - 2)
        parent1_list = list(parent1["branches"].values())
        parent2_list = list(parent2["branches"].values())
        parent1_list, parent2_list = ([parent1_list[:xo_point] + parent2_list[xo_point:],
                parent2_list[:xo_point] + parent1_list[xo_point:]])
        
        parent1["branches"] = dict(zip(list(parent1["branches"].keys()), parent1_list))
        parent2["branches"] = dict(zip(list(parent2["branches"].keys()), parent2_list))
        return (parent1, parent2)
    
    # mutation
    def mutation(self, individual, k_mut = 0.1):

        for task, i in individual["branches"].items():
            b_range = len(self.process_allocation.allocations[task.attrib['id']].branches)-1
            if random.random() < k_mut and b_range > 0:
                while True:
                    no = random.randint(0, b_range)
                    if no != i:
                        break
                individual["branches"][task] = no
        return copy.copy(individual)

    def build_solution(self, ind, measure="cost", rtype="solution"):
        return self.fitness(ind, measure, rtype)   
    
    def evolve(self, ev_type, population, fitnesses, gen):

        localizer={
            "plain" : self.plain_evolve,
            "random" : self.random_insert_evolve,
            "parent" : self.parent_evolve,
            "randomparent" : self.random_parent_evolve,
            "elitist" : self.elitist_evolve

        }
        return localizer[ev_type](population, fitnesses, gen)
    
    def plain_evolve(self, population, fitnesses, gen):

        nextgen_population = []
        for i in range(int(self.pop_size / 2)):
            parent1, xo1 = self.selection(population, fitnesses, gen)  # select first parent
            parent2, xo2 = self.selection(population, fitnesses, gen)  # select second parent

            offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
            nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)] # mutate offspring
       
        return nextgen_population    

    def random_insert_evolve(self, population, fitnesses, gen):
            
        nextgen_population = []

        for i in range(int(self.pop_size / 2)-2): # keep to spaces open for random individuals
            parent1, xo1 = self.selection(population, fitnesses, gen)  # select first parent
            parent2, xo2 = self.selection(population, fitnesses, gen)  # select second parent

            offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
            nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)]    # mutate offspring

        nextgen_population += [{"branches" : self.build_individual(), "branches": self.build_individual()}]     # insert 2 new random individuals
        return nextgen_population
    
    def parent_evolve(self, population, fitnesses, gen):
        
        nextgen_population = []
        for i in range(int(self.pop_size / 2)):
            parent1, xo1 = self.selection(population, fitnesses, gen)  # select first parent
            parent2, xo2 = self.selection(population, fitnesses, gen)  # select second parent
            if xo1 or xo2:
                nextgen_population +=  [parent1, parent2]

            else:
                offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
                nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)] # mutate offspring

        return nextgen_population
    
    
    def elitist_evolve(self, population, fitnesses, gen):
        
        # top_two_fitnesses: 
        top_indices = np.argsort(fitnesses)[:2]
        nextgen_population = [copy.copy(population[i]) for i in top_indices]

        for i in range(int(self.pop_size / 2) - 2):
            parent1, xo1 = self.selection(population, fitnesses, gen)  # select first parent
            parent2, xo2 = self.selection(population, fitnesses, gen)  # select second parent

            offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
            nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)] # mutate offspring

        return nextgen_population

    def random_parent_evolve(self, population, fitnesses, gen):
            
            nextgen_population = []
            for i in range(int(self.pop_size / 2)-2):
                parent1, xo1 = self.selection(population, fitnesses, gen)  # select first parent
                parent2, xo2 = self.selection(population, fitnesses, gen)  # select second parent
                if xo1 or xo2:
                    nextgen_population +=  [parent1, parent2]

                else:
                    offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
                    nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)] # mutate offspring
                
            nextgen_population += [{"branches" : self.build_individual(), "branches": self.build_individual()}]
            return nextgen_population
         
    
    def find_solutions(self, ev_type, measure):

        data = defaultdict(list)
        data["solver"].append(ev_type)
        population = self.init_population(self.pop_size) #, self.genome_size) -> genome_size = size of process
        unique_solutions = []
        start = time.time()     # Start of evolution
        for gen in range(self.generations):
            
            [unique_solutions.append(list(individual["branches"].values())) for individual in population if list(individual["branches"].values()) not in unique_solutions]
            fitnesses = [self.fitness(individual, measure) for individual in population]
            population = self.evolve(ev_type, population, fitnesses, gen) # Next Evolution Step

            # write data per generation
            data["fitnesses"].append(fitnesses)
            data["avg_fit"].append(sum(fitnesses)/len(fitnesses))
            data["min_fit"].append(min(fitnesses))
            data["max_fit"].append(max(fitnesses))
            data["unique_solutions"].append(unique_solutions)
            
            abandon_after = 11
            if self.early_abandon and gen > abandon_after:
                arr = np.array(data["min_fit"][-11:])
                if np.all(np.equal(arr, arr[0])):
                    print(f"Stopped after {gen} iterations")
                    break
        end = time.time()

        # write data for whole search
        data["time"].append(end-start)
        data["best"].append(self.best_tournament[-1])

        # add solutions to population
        fin_pop = []
        for ind in population:
            ind["solution"] = self.build_solution(ind, measure=measure)
            ind[measure] = ind["solution"].get_measure(measure)
            ind.pop("branches")
            fin_pop.append(ind)
        
        #TODO Check if whole population is invalid
        fin_pop = sorted(fin_pop, key=lambda d: d['cost'], reverse=True) 
        
        return fin_pop, data

class Heuristic():
    pass

class Brute(SolutionSearch):
    def __init__(self, process_allocation):
        super(Brute, self).__init__(process_allocation)
        self.pickle_writer = 0
    
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
        task = get_next_task(tasks_iter, solution)
        if task == "end":
            return
        
        allocation = self.process_allocation.allocations[task.attrib['id']]

        for i, branch in enumerate(allocation.branches):
            if i > 0:
                new_solution = copy.deepcopy(solution)
                self.solutions.append(new_solution)
            else: 
                solution_index=len(self.solutions)-1

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
            self.find_solutions(copy.deepcopy(tasks_iter), solution)
    
    def find_solutions_with_heuristic(self, tasks_iter=None, solution=None, measure="cost", top_n=1):
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
            return self.find_solutions_with_heuristic(iter(tasklist), self.solutions[0], top_n=top_n)
        
        # Find next task for solution
        task = get_next_task(tasks_iter, solution)
        if task == "end":
            return
        
        allocation = self.process_allocation.allocations[task.attrib['id']]

        # select top n branches
        indices = np.argsort([branch.get_measure(measure, operator=sum) for branch in allocation.branches])[:top_n]
        used_branches = [allocation.branches[i] for i in indices]
        #print(f"used_branches: {used_branches}")

        for i, branch in enumerate(used_branches):
            if i > 0:
                new_solution = copy.deepcopy(solution)
                self.solutions.append(new_solution)
            else: 
                solution_index=len(self.solutions)-1

        #TODO if less branches should be used: lower the amount of allocation.branches here
        for i, branch in enumerate(used_branches):
            #TODO Delete Solution if error in Change Operation
            if i > 0:
                solution = self.solutions[solution_index + i]
            #TODO ensure that label is the same too
            tasklabel = R_RPST.get_label(etree.tostring(task))
            task = solution.process.xpath(f"//*[@id='{task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=ns)[0]

            if branch.valid == False:
                solution.invalid_branches = True
            
            solution.process = branch.apply_to_process(solution.process, solution, task)
            self.find_solutions_with_heuristic(copy.deepcopy(tasks_iter), solution, top_n=top_n)
    
   
    def get_all_opts(self):
        #TODO should be callable with different options (Direct, Genetic, Heuristic, SemiHeuristic)
        """
        -> Add all Branches as new solutions
        -> for each branch, call, "new_solution(process, self, step+=1)"
        -> if i > 1: copy current solution and add new solution
        End: no further step
        """
        ns = {"cpee1" : list(self.process_allocation.process.nsmap.values())[0]}
        tasklist = self.process_allocation.process.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=ns)
        # choose random branch per task:
        translation = {task: str(uuid.uuid1()) for i, task in enumerate(tasklist)}
        
        all_opts = []
        for task in tasklist: 
            allocation = self.process_allocation.allocations[task.attrib['id']]
            all_opts.append({translation[task] : [i for i in range(len(allocation.branches))]})
        
        self.solution_space_size = np.prod([len(allocation.branches) for allocation in self.process_allocation.allocations.values()])
    
        return all_opts, tasklist

        # approach with itertools.product: 
    
    def find_best_solution_bb(self, solutions, measure):
        best_solutions = [] 
        len(solutions)
        for i, solution in enumerate(solutions):
            
            new_solution = Solution(copy.deepcopy(self.process)) # create solution
            ns = {"cpee1" : list(new_solution.process.nsmap.values())[0]}
            tasklist = new_solution.process.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=ns)
            individual = {tasklist[i]: list(solution)[i] for i in range(len(solution))}
            tasks_iter = iter(tasklist) # iterator
            task = get_next_task(tasks_iter, new_solution) # gets next tasks and checks for deletes

            while True:
                allocation = self.process_allocation.allocations[task.attrib['id']] # get allocatin

                branch_no = individual.get(task)    # get choosen number of branch
                branch = allocation.branches[branch_no] # get actual branch as R-RPST

                new_solution.process = branch.apply_to_process(new_solution.process, solution=new_solution) # build branch
                
                task = get_next_task(tasks_iter, new_solution)
                if task == "end":
                    break
            
            new_solution.check_validity()
            if new_solution.invalid_branches:
                value = np.nan        
            else:
                value = copy.deepcopy(new_solution.get_measure(measure))   # calc. fitness of solution
                value = float(copy.deepcopy(value))
            if value != np.nan:
                if not best_solutions:
                    best_solutions.append({"cost": value})             
                elif (value < best_solutions[-1].get("cost") or not best_solutions) and value != np.nan:
                    best_solutions.append({"cost": value})
            print(f"Done : {i}/{len(solutions)}")

        return best_solutions

    def retrieve_pickle(self, file_path):
        data = []
        file = open(file_path, 'rb') 
        data.append(pickle.load(file))
        file.close()

        return data

    def iter_product(self, arr):
        a = []
        for x in itertools.product(*arr):
            a.append(x)
        
        print("No of Solutions: ", len(a))
        return a

    def get_best_solutions(self, measure, operator=min, include_invalid=True, top_n=1):
        #TODO get_best_solutions in parent class
        solutions_to_evaluate = filter(self.solutions) if include_invalid else filter(lambda x: x.invalid_branches == False, self.solutions)
        a = list(solutions_to_evaluate)
        solution_measure = {solution: solution.get_measure(measure) for solution in a}

        # Get the top N solutions
        #sorted_solutions = sorted(solution_measure.items(), key=lambda x: x[1], reverse=(operator == max))
        sorted_solutions = np.argsort(list(solution_measure.values()))[:top_n]
        #top_solutions = [solution for solution, _ in sorted_solutions[:top_n]]
        sorti = list(sorted_solutions)
        top_solutions = [a[i] for i in sorti]
        #fin = [{solution: solution.get_measure("cost")} for solution in top_solutions]
        fin_pop = [{"solution": solution, "cost": solution.get_measure("cost")} for solution in top_solutions]
        
        fin_pop = sorted(fin_pop, key=lambda d: d['cost'], reverse=True) 
        return fin_pop
    
    def find_solutions_ab(self, solutions, measure):

        pool = mp.Pool()
        results = []
        num_parts = mp.cpu_count()
        #num_parts = 1
        part_size = len(solutions) // num_parts
        args = []
        list_parts = []
        with open("tmp/process.pkl", "wb") as f: 
            pickle.dump(etree.tostring(self.process), f)
        with open("tmp/allocations.pkl", "wb") as f:
            for allocation in self.process_allocation.allocations.values():
                allocation.process = 0
                allocation.parent = 0 
                allocation.intermediate_trees = [etree.tostring(tree) for tree in allocation.intermediate_trees]
                for branch in allocation.branches:
                    branch.node = etree.tostring(branch.node)

            pickle.dump(self.process_allocation.allocations, f)


        list_parts = [solutions[part_size * i : part_size * (i + 1)] for i in range(num_parts)]

        # Use starmap instead of map
        results = pool.map(find_best_solution_bb, [(part, measure, i) for i, part in enumerate(list_parts)])
        #results.wait()
        #output = results.get
        pool.close()
        pool.join()
        
        best_solutions = []

def solution_search_factory():
    pass

def find_best_solution_bb(solutions): # ,measure, n):
    solutions, measure, n = solutions
    with open("tmp/process.pkl", "rb") as f:
        process  = etree.fromstring(pickle.load(f))
    with open("tmp/allocations.pkl", "rb") as f:
        allocations = pickle.load(f)
        for allocation in allocations.values():
            allocation.task = etree.fromstring(allocation.task)
            for branch in allocation.branches:
                branch.node = etree.fromstring(branch.node)

    
    best_solutions = [] 
    start = time.time()
    for i, solution in enumerate(solutions):
        
        new_solution = Solution(copy.deepcopy(process)) # create solution
        ns = {"cpee1" : list(new_solution.process.nsmap.values())[0]}
        tasklist = new_solution.process.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=ns)
        individual = {tasklist[i]: list(solution)[i] for i in range(len(solution))}
        tasks_iter = iter(tasklist) # iterator
        task = get_next_task(tasks_iter, new_solution) # gets next tasks and checks for deletes

        while True:

            allocation = allocations[task.attrib['id']] # get allocatin
            branch_no = individual.get(task)    # get choosen number of branch
            branch = allocation.branches[branch_no] # get actual branch as R-RPST
            new_solution.process = branch.apply_to_process(new_solution.process, solution=new_solution) # build branch
            task = get_next_task(tasks_iter, new_solution)
            if task == "end":
                break

        new_solution.check_validity()
        if new_solution.invalid_branches:
            value = np.nan        
        else:
            value = copy.deepcopy(new_solution.get_measure(measure, flag=True))   # calc. fitness of solution
            value = float(copy.deepcopy(value))
        if value != np.nan:
            if not best_solutions:
                best_solutions.append({"solution": new_solution, "cost": value})             
            elif (value < best_solutions[-1].get("cost") or not best_solutions) and value != np.nan:
                best_solutions.append({"solution": new_solution, "cost": value})
                if len(best_solutions) > 10:
                    best_solutions.pop(0)
     
        if i%1000 == 0:
            end = time.time()
            print(f"{i}/{len(solutions)}, Time: {(end-start):.2f}")
            start = time.time()
    
    dump_to_pickle(best_solutions, n)
    return (f"done_{n}")

def dump_to_pickle(solution, i):
    for x in solution:
        x["solution"].process = etree.tostring(x["solution"].process)


    with open(f"tmp/results/results_{i}.pkl", "wb") as f:
        pickle.dump(solution, f)

def combine_pickles(folder_path="tmp/results"):
    print("combine_pickles")
    
    files = os.listdir(folder_path)
    best_solutions = []
    for file in files:
        file_path = folder_path + "/" + file
        if os.path.isdir(file_path):
            continue
        
        with open(file_path, "rb") as f:
            dd = pickle.load(f)
        for d in dd:
            if best_solutions:
                if d.get("cost") < best_solutions[0].get("cost"): best_solutions.append(d) 
                best_solutions = sorted(best_solutions, key=lambda d: d['cost'], reverse=True) 
                if len(best_solutions) > 10: best_solutions.pop(0)
            else:
                best_solutions.append(d)
    return best_solutions


