# Import modules
from tree_allocation.allocation.cpee_allocation import *
from tree_allocation.tree import R_RPST

# Import external packages
from lxml import etree
import numpy as np
import random
import time

class SolutionSearch():
    def __init__(self, process_allocation):
        self.solutions = []
        self.process_allocation = process_allocation
        self.process = process_allocation.process
        self.ns = {"cpee1" : list(self.process.nsmap.values())[0]}

class Genetic(SolutionSearch):
    def __init__(self, process_allocation, pop_size, generations):
        super(Genetic, self).__init__(process_allocation)
        self.pop_size = pop_size
        #TODO Genome = Process that is to be allocated/changed
        #self.genome_size = genome_size
        self.generations = generations
        
    def init_population(self, pop_size): #, genome_size): initialize the population of bit vectors
        #TODO create random solutions with number of pop_size
        string = open("check_p").read()
        if not etree.tostring(self.process) == open("check_p", "rb").read():
            raise "Problem"
        population = []
        self.tasklist = self.process_allocation.process.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns)
        with open("check_p", "wb") as f:
            f.write(etree.tostring(self.process))
        
        for pop in range(pop_size):   
            # choose random branch per task:
            proc = copy.deepcopy(self.process)
            solution = Solution(proc)
            used_branches = {}
            for task in self.tasklist:
                allocation = self.process_allocation.allocations[task.attrib['id']]
                branch_no = random.randint(0, len(allocation.branches)-1)
                used_branches[task] = branch_no
                branch = allocation.branches[branch_no]
                solution.process = branch.apply_to_process(proc, solution=solution)
        
            population.append({"solution":solution, "branches" : used_branches})
        


        return population
    
    def fitness(self, solution, measure):
        #TODO fitness = measure of the solution
        return solution.get_measure(measure)
    
    # tournament selection
    def selection(self, population, fitnesses, k=3):
        # keep the best solution
        # first random selection
        tournament = random.sample(range(len(population)-1), k=3)
        tournament_fitnesses = [fitnesses[i] for i in tournament]
        winner_index = tournament[np.argmin(tournament_fitnesses)]
        return population[winner_index]
    
    def crossover(self, parent1, parent2): 
        #TODO Split the process and cross between the two parents
        # whats the best approach for handovers?
        proc_len = len(parent1.values())
        xo_point = random.randint(1, proc_len - 1)
        parent1_list = list(parent1["branches"].values())
        parent2_list = list(parent2["branches"].values())
        ([parent1_list[:xo_point] + parent2_list[xo_point:],
                 parent2_list[:xo_point] + parent1_list[xo_point:]])
        
        parent1["branches"], parent2["branches"] = (dict(zip(list(parent1["branches"].keys()), parent1_list)), 
                                                        dict(zip(list(parent2["branches"].keys()), parent2_list)))
        return (parent1, parent2)
    
    def mutation(self, individual):
        #TODO change allocation randomly on one task
        #for i in range(len(individual["used_branches"])):
        #    if random.random() < 0.1:
        #        individual["used_branches"] = individual["used_branches"][:i] + [1-individual["used_branches"][i]] + individual["used_branches"][i + 1:]
        return individual
    
    def evaluate_solution(self, individual):
        proc = copy.deepcopy(self.process)
        i=0

        new_solution = Solution(proc)
        new_solution.process = copy.deepcopy(self.process)

        if i ==1: 
            with open("xml2_out.xml", "wb") as f:
                f.write(etree.tostring(proc))
            with open("xml3_out.xml", "wb") as f:
                f.write(etree.tostring(self.process))

        for task in self.tasklist:
            allocation = self.process_allocation.allocations[task.attrib['id']]
            branch_no = individual["branches"].get(task)
            branch = allocation.branches[branch_no]
            #graphix.TreeGraph().show(etree.tostring(branch.node), filename="branch") 

                
            branch.apply_to_process(proc, solution=new_solution)
        
        new_solution.process = copy.deepcopy(proc)

        return {"solution":new_solution, "branches" : individual["branches"]}
    
    def find_solutions(self, measure):
        #TODO change for process setting
        population = self.init_population(self.pop_size) #, self.genome_size) -> genome_size = size of process
        for gen in range(self.generations):
            start = time.time()
            fitnesses = [self.fitness(individual["solution"], measure) for individual in population]
            print('Generation ', gen, '\n', list(zip(population, fitnesses)))
            nextgen_population = []
            for i in range(int(self.pop_size / 2)):
                parent1 = self.selection(population, fitnesses)  # select first parent
                parent2 = self.selection(population, fitnesses)  # select second parent
                offspring1, offspring2 = self.crossover(parent1, parent2)  # perform crossover between both parents

                # create new solutions and calculate measure
                nextgen_population.append(self.evaluate_solution(offspring1))
                nextgen_population.append(self.evaluate_solution(offspring2))
                #nextgen_population += [self.mutation(offspring1), self.mutation(offspring2)]  # mutate offspring

            population = nextgen_population
            end = time.time()
            print(f"Time for genereation: {end-start}")
        return population

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
            
            branch.apply_to_process(solution.process, solution, task)
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