# Import modules
from src.allocation.cpee_allocation import *
from src.allocation.solution import Solution
from src.tree import R_RPST
from src.allocation.utils import get_next_task

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
        self.process_allocation = etree.fromstring(process_allocation)
        #self.process = process_allocation.process
        self.ns = {"cpee1" : list(self.process_allocation.nsmap.values())[0]}

class Genetic(SolutionSearch):

    def __init__(self, process_allocation, pop_size, generations, k_sel=3, k_mut=0.1, early_abandon=True):
        super(Genetic, self).__init__(process_allocation)
        self.pop_size:int = pop_size
        self.generations:int = generations
        self.k_mut:float = k_mut
        self.k_sel:int = k_sel
        self.best_tournament = [1000]
        self.best_tournament_str:str = []
        self.early_abandon:bool=early_abandon
        
    def init_population(self): #, genome_size): initialize the population of bit vectors
        # create random solutions for number of pop_size

        population = []
        self.tasklist = self.process_allocation.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns)
        for pop in range(self.pop_size): 
            solution = Solution(copy.deepcopy(self.process_allocation))
            to_apply = self.build_individual(solution)
            population.append(solution)
        return population

    def build_individual(self, solution):
        # choose random branch per task:

        # build randomly a solution pattern [1,4,2,3,...]
        # TODO: create this out of class RA_PST with "Get possible branches"

        possible_branches = solution.get_possible_branches()
        used_branches = [random.randint(0, i) for  i in possible_branches]
        solution.branches_to_apply = used_branches
        return used_branches
    
    def fitness(self, solution,  measure:str="cost", rtype:str = "value"):
        # calculate the fitness of a solution
        individual = solution.branches_to_apply

        if not solution.is_final:
            solution.apply_branches(individual)
        solution.check_validity()
        value = solution.get_measure(measure)   # if solution is invalid, value = np.nan

        if rtype=="solution":
            return solution
        else:
            return value
    
    # tournament selection
    def selection(self, population, fitnesses, gen):
        #TODO improve dealing with invalid solutions
        
        xo = False # init xo flag

        tournament = random.sample(range(len(population)-1), self.k_sel)
        tournament_fitnesses = [fitnesses[i] for i in tournament]

        try:
            winner_index = tournament[np.nanargmin(tournament_fitnesses)]
        except ValueError:
            winner_index = tournament[np.argmin(tournament_fitnesses)]
 
        if fitnesses[winner_index] <= self.best_tournament[-1]:

            self.best_tournament.append(fitnesses[winner_index])
            xo = True # flag to keep as elitist parent

        return copy.copy(population[winner_index]), xo
    
    # parent crossover
    def crossover(self, parent1, parent2): 
        parent1, parent2 = (copy.deepcopy(parent1), copy.deepcopy(parent2))

        proc_len = len(parent1.branches_to_apply)
        xo_point = random.randint(1, proc_len - 2)
        parent1_list = list(parent1.branches_to_apply)
        parent2_list = list(parent2.branches_to_apply)
        #parent1_list, parent2_list = 
        
        offspring1, offspring2 = Solution(parent1.init_ra_pst), Solution(parent2.init_ra_pst)
        offspring1.branches_to_apply, offspring2.branches_to_apply = ([parent1_list[:xo_point] + parent2_list[xo_point:],
                parent2_list[:xo_point] + parent1_list[xo_point:]])
        return (offspring1, offspring2)
    
    # mutation
    def mutation(self, solution, k_mut = 0.1):

        for i in range(len(solution.branches_to_apply)):
            b_range = solution.get_possible_branches()[i]
            if random.random() < k_mut and b_range > 0:
                while True:
                    no = random.randint(0, b_range)
                    if no != i:
                        break
                solution.branches_to_apply[i] = no
        return solution

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
        """not in use"""    
        nextgen_population = []

        for i in range(int(self.pop_size / 2)-2): # keep to spaces open for random individuals
            parent1, xo1 = self.selection(population, fitnesses, gen)  # select first parent
            parent2, xo2 = self.selection(population, fitnesses, gen)  # select second parent

            offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
            nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)]    # mutate offspring

        nextgen_population += [{"branches" : self.build_individual(), "branches": self.build_individual()}]     # insert 2 new random individuals
        return nextgen_population
    
    def parent_evolve(self, population, fitnesses, gen):
        """not in use"""            
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
        print([(solution, solution.get_measure("cost")) for solution in nextgen_population])
        for i in range(int((self.pop_size-2) / 2)):
            parent1, xo1 = self.selection(population, fitnesses, gen)  # select first parent
            parent2, xo2 = self.selection(population, fitnesses, gen)  # select second parent

            offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents
            nextgen_population += [self.mutation(offspring1, k_mut=self.k_mut), self.mutation(offspring2, k_mut=self.k_mut)] # mutate offspring

        return nextgen_population

    def random_parent_evolve(self, population, fitnesses, gen):
        """not in use"""                
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
         
    
    def find_solutions(self, ev_type, measure): #TODO should probably move into RA_PST.

        data = defaultdict(list)
        data["solver"].append(ev_type)
        population = self.init_population() #, self.genome_size) -> genome_size = size of process
        unique_solutions = []
        start = time.time()     # Start of evolution
        for gen in range(self.generations):
            
            #TODO irgendwo hier verschmeißt er die Elite solutions
            #[unique_solutions.append(list(individual["branches"].values())) for individual in population if list(individual["branches"].values()) not in unique_solutions]
            [unique_solutions.append(list(solution.branches_to_apply)) for solution in population if list(solution.branches_to_apply) not in unique_solutions]  
            fitnesses = [self.fitness(solution, measure) for solution in population]
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
        fitnesses = [self.fitness(solution, measure) for solution in population]

        # write data for whole search
        data["time"].append(end-start)
        data["best"].append(self.best_tournament[-1])

        # add solutions to population
        fin_pop = []
        for solution in population:
            fin_pop.append({"solution": solution, str(measure): solution.get_measure(measure)})
        
        #TODO Check if whole population is invalid
        fin_pop = sorted(fin_pop, key=lambda d: d['cost'], reverse=True) 
        
        return fin_pop, data

class Brute(SolutionSearch):
    def __init__(self, process_allocation):
        super(Brute, self).__init__(process_allocation)
        self.pickle_writer = 0

    def find_solutions_with_heuristic(self, tasks_iter=None, solution=None, measure="cost", top_n=1, force_valid=True):
        #TODO should be callable with different options (Direct, Genetic, Heuristic, SemiHeuristic)
        """
        -> Add all Branches as new solutions
        -> for each branch, call, "new_solution(process, self, step+=1)"
        -> if i > 1: copy current solution and add new solution
        End: no further step
        """
        branches = []
        solution = Solution(copy.deepcopy(self.process_allocation))

        for task in solution.task_list:
            # Create list of branches to try: 

            possible_branches = solution.get_branches_for_task_wrap(task)
            if force_valid:
                possible_branches = [branch for branch in possible_branches if branch.is_valid]
            
            branches.append(np.argsort([branch.get_measure(measure, operator=sum) for branch in possible_branches])[:top_n])
            print(branches)

        possible_solutions = self.iter_product(branches)
        
        for solution_branches in possible_solutions:
            new_solution = Solution(copy.deepcopy(self.process_allocation)) # create solution
            new_solution.branches_to_apply = list(solution_branches)

            new_solution.apply_branches(new_solution.branches_to_apply)            
            new_solution.check_validity()

            value = new_solution.get_measure(measure)   # calc. fitness of solution
            self.solutions.append(new_solution)
        
        return [{"solution": solution, str(measure): solution.get_measure(measure)} for solution in self.solutions] 
        
   
    def get_all_opts(self):
        #TODO should be callable with different options (Direct, Genetic, Heuristic, SemiHeuristic)
        """
        -> Add all Branches as new solutions
        -> for each branch, call, "new_solution(process, self, step+=1)"
        -> if i > 1: copy current solution and add new solution
        End: no further step
        """
        ns = {"cpee1" : list(self.process_allocation.nsmap.values())[0]}
        solution = Solution(self.process_allocation)
        #tasklist = self.process_allocation.process.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=ns)
        # choose random branch per task:
        translation = {task: str(uuid.uuid1()) for i, task in enumerate(solution.task_list)}
        
        all_opts = []
        for task in solution.task_list: 
            #allocation = self.process_allocation.allocations[task.attrib['id']]
            all_opts.append({translation[task] : [i for i in range(len(solution.get_branches_for_task_wrap(task)))]})
        
        self.solution_space_size = np.prod([len(solution.get_branches_for_task_wrap(task)) for task in solution.task_list])
    
        return all_opts, solution.task_list

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
        solutions_to_evaluate = self.solutions if include_invalid else filter(lambda x: (x.invalid_branches == False), self.solutions)
        a = list(solutions_to_evaluate)
        solution_measure = {solution: solution.get_measure(measure) for solution in a}

        # Get the top N solutions
        sorted_solutions = np.argsort(list(solution_measure.values()))[:top_n]
        sorti = list(sorted_solutions)
        top_solutions = [a[i] for i in sorti]
        fin_pop = [{"solution": solution, "cost": solution.get_measure("cost")} for solution in top_solutions]
        
        fin_pop = sorted(fin_pop, key=lambda d: d['cost'], reverse=True) 
        if not fin_pop:
            raise NoSolutionError
        return fin_pop
    
    def find_solutions(self, solutions, measure):

        pool = mp.Pool()
        results = {1:[]}
        num_parts = mp.cpu_count()
        part_size = len(solutions) // num_parts
        args = []
        list_parts = []
        
        folder_name = 'tmp'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            os.makedirs(folder_name + "/results")
        
        with open("tmp/process.pkl", "wb") as f: 
            pickle.dump(etree.tostring(self.process_allocation), f)
        
        with open("tmp/ra_pst.pkl", "wb") as f: 
            pickle.dump(etree.tostring(self.process_allocation), f)

        list_parts = [solutions[part_size * i : part_size * (i + 1)] for i in range(num_parts)]

        results[1] = pool.map(find_best_solution, [(part, measure, i) for i, part in enumerate(list_parts)])
        pool.close()
        pool.join()
        print(results [1])

def find_best_solution(solutions): # ,measure, n):
    solution_branches, measure, n = solutions
    with open("tmp/process.pkl", "rb") as f:
        process  = etree.fromstring(pickle.load(f))
    with open("tmp/ra_pst.pkl", "rb") as f:
        ra_pst  = etree.fromstring(pickle.load(f))
    
    best_solutions = [] 
    start = time.time()
    for i, individual in enumerate(solution_branches):
        
        new_solution = Solution(copy.deepcopy(ra_pst)) # create solution
        new_solution.branches_to_apply = list(individual)
        new_solution.apply_branches(new_solution.branches_to_apply)
        new_solution.check_validity()

        value = new_solution.get_measure(measure, flag=False)   # calc. fitness of solution
        

        if not np.isnan(value) :
            if not best_solutions:
                best_solutions.append({"solution": new_solution, "cost": value})             
            elif (value < best_solutions[0].get("cost") or np.isnan(best_solutions[0].get("cost"))) and not np.isnan(value):
                best_solutions.append({"solution": new_solution, "cost": value})
                best_solutions = sorted(best_solutions, key=lambda d: d[measure], reverse=True) 
                if len(best_solutions) > 25:
                    best_solutions.pop(0)
     
        if i%1000 == 0:
            end = time.time()
            print(f"{i}/{len(solution_branches)}, Time: {(end-start):.2f}")
            start = time.time()
    
    print("Best solutions: ", best_solutions)
    dump_to_pickle(best_solutions, n)
    return (f"done_{n}")

def combine_pickles(folder_path="tmp/results", measure="cost"):
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
                if d.get("cost") < best_solutions[0].get(measure) or np.isnan(best_solutions[0].get(measure)): 
                    best_solutions.append(d) 
                best_solutions = sorted(best_solutions, key=lambda d: d[measure], reverse=True) 
                if len(best_solutions) > 10: 
                    best_solutions.pop(0)
            else:
                best_solutions.append(d)
    return best_solutions
    

def dump_to_pickle(solution, i):
    for x in solution:
        x["solution"] = x["solution"].get_pickleable_object()



    with open(f"tmp/results/results_{i}.pkl", "wb") as f:
        pickle.dump(solution, f)

class NoSolutionError(Exception):
    "Raised when no Solution can be found with the given configuration"
    pass
