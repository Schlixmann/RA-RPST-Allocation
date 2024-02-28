from context import src
import unittest
from lxml import etree
from xmldiff import main, formatting
from src.tree import parser, task_node as tn, gtw_node as gtw
from src.allocation import cpee_allocation
from pptree import *
from PrettyPrint import PrettyPrintTree
from src.tree import graphix
from src.allocation.solution_search import *
import time


class TestCpeeAllocation(unittest.TestCase):
    def test_heuristic_solution(self):
        with open("resource_config/offer_resources.xml") as f: 
                resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process.xml") as f:
                task_xml = f.read()
        show_graph = False
            
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        trees = ProcessAllocation.allocate_process()

        allocation = list(ProcessAllocation.allocations.values())[0]
        allocation.branches
        for i, tree in enumerate(list(trees.values())):   
            
            if show_graph:
                graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"out_{i}") 

        start = time.time()
        brute_solutions = Brute(ProcessAllocation)
        brute_solutions.find_solutions_with_heuristic( measure="cost", top_n=1)
        end = time.time()

        print("Number of Solutions: {}".format(len(brute_solutions.solutions)))
        print("Solutions found in: {} s".format(end-start))

        measure = "cost"
        ProcessAllocation.solutions = brute_solutions.solutions
        best_solutions = brute_solutions.get_best_solutions(measure, include_invalid=False, top_n=5)
        print(best_solutions)

        #for i, solution in enumerate(best_solutions):
        #    with open(f"tests/benchmarks/best_brute_{i}.xml", "wb") as f:
        #        key = next(iter(solution))
        #        f.write(etree.tostring(key.process))             
        
        for i, solution in enumerate(best_solutions):
            with open(f"tests/solutions/test_heu_short_proc_{i}.xml", "wb") as f:
                f.write(etree.tostring(list(solution.keys())[0].process))
