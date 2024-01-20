import unittest
from lxml import etree
from pptree import *
import time

from tree_allocation.allocation.solution_search import Genetic
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
        with open("tests/test_processes/offer_process_short.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = ProcessAllocation.allocate_process()

        start = time.time()
        genetic_solutions = Genetic(ProcessAllocation, pop_size=5, generations=100)
        gen = genetic_solutions.find_solutions("cost")
        end = time.time()

        print(gen)
        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(gen[0]["solution"].process))

