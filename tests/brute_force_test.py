import unittest
from lxml import etree
from pptree import *
import time
import random
from collections import defaultdict
import json

from src.allocation.solution_search import Genetic,Brute
from src.allocation.cpee_allocation import ProcessAllocation
from src.allocation.solution_search import *
from src.tree import parser, task_node as tn, gtw_node as gtw
from src.allocation import gen_deap
from src.tree import graphix

class BruteForceTest(unittest.TestCase):
    
    def test_genetic_new_approach(self):
        with open("resource_config/offer_resources_close_maxima.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_paper.xml") as f:
            task_xml = f.read()
        
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)    
        process_allocation.allocate_process()

        process_allocation.solver = Genetic(process_allocation.ra_rpst, pop_size=25, generations=25, k_mut=0.2)
        start = time.time()
        population, data = process_allocation.solver.find_solutions('elitist', "cost")
        end = time.time()
        gen_time = end - start
        
        for individual in population:
            print("Branches: ", individual["solution"].allocated_branches)
            print("Solution Costs: ", individual["solution"].get_measure("cost"))
        print("Gen_time: ", gen_time)
        print(process_allocation.solver.best_tournament)

        #print(population)
        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(population[-1]["solution"].solution_ra_pst))
        print("done")


    def test_brute_solution(self):
        out_folder="tests/results/experiments"

        with open("resource_config/offer_resources_close_maxima.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_short.xml") as f:
            task_xml = f.read()
        
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)    
        process_allocation.allocate_process()

        process_allocation.solver = Brute(process_allocation.ra_rpst)
        measure = "cost"
        start = time.time()

        solutions, tasklist = process_allocation.solver.get_all_opts()
        solutions = [list(o.values())[0] for o in solutions]
        num_brute_solutions = process_allocation.solver.iter_product(solutions)

        results = process_allocation.solver.find_solutions(num_brute_solutions, measure)
        
        outcome = combine_pickles()
        end = time.time()
        print(outcome)

        performance_brute = defaultdict(list)
        performance_brute["solver"].append("brute")
        performance_brute["size"].append(len(num_brute_solutions))
        performance_brute["time"].append(float(end-start))
        performance_brute["items"]= [[solution[measure] for solution in outcome]]
        performance_brute["best"].append(outcome[-1][measure])


        with open(out_folder + "/brute_results_paper.json", "w") as f:
            json.dump(performance_brute, f)
        with open(out_folder + "/proc/brute.xml", "wb") as f:
            f.write(outcome[-1]["solution"].solution_ra_pst)

        print(f"Time: {end-start}")
        print("Invalid Branches? ", [ind["solution"].invalid_branches for ind in outcome])
