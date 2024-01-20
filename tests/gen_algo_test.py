import unittest
from lxml import etree
from pptree import *
import time

from tree_allocation.allocation.solution_search import Genetic,Brute
from tree_allocation.allocation import cpee_allocation
from tree_allocation.tree import parser, task_node as tn, gtw_node as gtw

class TestGenetic(unittest.TestCase):
    def test_genetic_base(self):
        ga = Genetic(10,10,50)
        outcome = ga.find_solution("bla")
        print(outcome)
    
    def test_init_pop(self):
        with open("resource_config/offer_resources.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = ProcessAllocation.allocate_process()

        start = time.time()
        genetic_solutions = Genetic(ProcessAllocation, pop_size=10, generations=100, k_mut=0.25)
        population = genetic_solutions.find_solutions("cost")
        end = time.time()
        gen_time = end - start
        
        for solution in population:
            print("Branches: ", solution["branches"].values())
            print("Solution Costs: ", solution["solution"].get_measure("cost"))
        print("Gen_time: ", gen_time)

        #print(population)
        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(population[0]["solution"].process))

    def test_gen_vs_brute_short(self):
        with open("resource_config/offer_resources.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_short.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = ProcessAllocation.allocate_process()

        start = time.time()
        genetic_solutions = Genetic(ProcessAllocation, pop_size=20, generations=100, k_mut=0.2)
        population = genetic_solutions.find_solutions("cost")
        end = time.time()
        gen_time = end - start
        
        start = time.time()
        brute_solutions = Brute(ProcessAllocation)
        brute_solutions.find_solutions()
        ProcessAllocation.solutions = brute_solutions.solutions
        best_solutions = brute_solutions.get_best_solutions("cost", include_invalid=False, top_n=5)
        end = time.time()
        brute_time = end - start
        
        for solution in population:
            print("Branches: ", solution["branches"].values())
            print("Solution Costs: ", solution["solution"].get_measure("cost"))
        print("Gen_time: ", gen_time)
        print(genetic_solutions.best_tournament)

        #print(population)
        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(population[0]["solution"].process))
        

        
        for i, solution in enumerate(best_solutions):
            key = next(iter(solution))
            print("Solution Costs: ", key.get_measure("cost"))
            with open(f"tests/solutions/best_brute_.xml", "wb") as f:
                f.write(etree.tostring(key.process))
        print("Brute_time: ", brute_time)
