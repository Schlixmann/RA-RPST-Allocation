# Import modules
from tree_allocation.allocation.cpee_allocation import *

# Import external packages
from lxml import etree

class SolutionSearch():
    pass

class Genetic():
    pass

class Heuristic():
    pass

class Brute():
        
    def find_solutions(self, process_allocation, solution=None, task=None):
        #TODO should be callable with different options (Direct, Genetic, Heuristic, SemiHeuristic)
        """
        -> Add all Branches as new solutions
        -> for each branch, call, "new_solution(process, self, step+=1)"
        -> if i > 1: copy current solution and add new solution
        End: no further step
        """
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


def solution_search_factory():
    pass