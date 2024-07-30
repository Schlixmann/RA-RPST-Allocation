import unittest
from lxml import etree
from pptree import *
import time
import random
from collections import defaultdict
import json

from src.allocation.solution_search import Genetic,Brute
from src.allocation.cpee_allocation import ProcessAllocation
from src.tree import parser, task_node as tn, gtw_node as gtw
from src.allocation import gen_deap
from src.tree import graphix

class TestGenetic(unittest.TestCase):
    
    def test_init_pop(self):
        with open("resource_config/offer_resources.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = ProcessAllocation.allocate_process()

        start = time.time()
        genetic_solutions = Genetic(ProcessAllocation, pop_size=25, generations=25, k_mut=0.2)
        population, data = genetic_solutions.find_solutions('plain', "cost")
        end = time.time()
        gen_time = end - start
        
        for solution in population:
            print("Branches: ", solution["branches"].values())
            print("Solution Costs: ", solution["solution"].get_measure("cost"))
        print("Gen_time: ", gen_time)
        print(genetic_solutions.best_tournament)

        #print(population)
        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(population[0]["solution"].process))

    def test_gen_vs_brute_short(self):
        with open("resource_config/offer_resources_plain_fully_synthetic_small.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_short.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = ProcessAllocation.allocate_process()

        start = time.time()
        genetic_solutions = Genetic(ProcessAllocation, pop_size=25, generations=25, k_mut=0.2)
        population, data = genetic_solutions.find_solutions("elitist", "cost")
        end = time.time()
        gen_time = end - start
        
        start = time.time()
        brute_solutions = Brute(ProcessAllocation)
        brute_solutions.find_solutions_with_heuristic(top_n=1)
        ProcessAllocation.solutions = brute_solutions.solutions
        best_solutions = brute_solutions.get_best_solutions("cost", include_invalid=False, top_n=5)
        end = time.time()
        brute_time = end - start
        
        for i, solution in enumerate(population):
            print(i, ". Branches: ", solution["branches"].values())
            print("Solution Costs: ", solution["solution"].get_measure("cost"))
        print("Gen_time: ", gen_time)

        #print(population)
        
        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(population[0]["solution"].process))
        

        
        for i, solution in enumerate(best_solutions):
            key = next(iter(solution))
            print("Brute Solution Costs: ", key.get_measure("cost"))
            with open(f"tests/solutions/best_brute_.xml", "wb") as f:
                f.write(etree.tostring(key.process))
        print("Brute_time: ", brute_time)


    def test_approaches(self):
        with open("resource_config/offer_resources_heterogen.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_paper.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        ProcessAllocation.allocate_process()

        findings = []
        solv_types = ["plain", "random", "randomparent", "parent", "elitist"]
        #solv_types = ["elitist"]
        for i, stype in enumerate(solv_types):
            
            findings.append(defaultdict(list))
            start = time.time()
            genetic_solutions = Genetic(ProcessAllocation, pop_size=25, generations=50, k_mut=0.2, early_abandon=True)
            population, data = genetic_solutions.find_solutions(stype, "cost")
            end = time.time()
            gen_time = end - start
            findings[i]["solver"].append(stype)
            findings[i]["time"].append(gen_time)
            findings[i]["best"].append(genetic_solutions.best_tournament[-1])
            findings[i]["no_unique_solutions"] = len(data["unique_solutions"])
            findings[i]["fitnesses"] = data["fitnesses"]
            findings[i]["avg_fit"] = data["avg_fit"]
            findings[i]["min_fit"] = data["min_fit"]
            findings[i]["max_fit"] = data["max_fit"]
            findings[i]["unique_solutions"] = data["unique_solutions"]
            with open(f"findings_{i}.json", "w") as f:
                json_object = json.dumps(findings[i], indent=4)
                f.write(json_object)


            
            print(f"{stype} Solutions:")
            for solution in population:
                #print("Branches: ", solution["branches"].values())
                print("Solution Costs: ", solution["solution"].get_measure("cost"))
            print("Gen_time: ", gen_time)

        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(population[0]["solution"].process))

    def test_cascade_delete(self):
        # TODO change resources to a change pattern with multiple inserted tasks
        with open("resource_config/offer_resources_cascade_del.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_short.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = ProcessAllocation.allocate_process()

        start = time.time()
        genetic_solutions = Genetic(ProcessAllocation, pop_size=25, generations=25, k_mut=0.2)
        population, data = genetic_solutions.find_solutions("plain", "cost")
        end = time.time()
        gen_time = end - start
        
        start = time.time()
        brute_solutions = Brute(ProcessAllocation)
        brute_solutions.find_solutions()
        ProcessAllocation.solutions = brute_solutions.solutions
        best_solutions = brute_solutions.get_best_solutions("cost", include_invalid=False, top_n=5)
        end = time.time()
        brute_time = end - start
        
        for i, solution in enumerate(population):
            print(i, ". Branches: ", solution["branches"].values())
            print("Solution Costs: ", solution["solution"].get_measure("cost"))
        print("Gen_time: ", gen_time)
        print(genetic_solutions.best_tournament)

        #print(population)
        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(population[0]["solution"].process))

    def test_random(self):
        # TODO change resources to a change pattern with multiple inserted tasks
        with open("resource_config/offer_resources_vary2_test.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_paper copy.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = ProcessAllocation.allocate_process()

        show = True
        for i, tree in enumerate(list(trees.values())):    
            if i > 0:
                show = False
            graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"blabla_{i}", view=show) 

        start = time.time()
        genetic_solutions = Genetic(ProcessAllocation, pop_size=25, generations=50, k_mut=0.2, early_abandon=True)
        population, data = genetic_solutions.find_solutions("elitist", "cost")
        print(population)
        end = time.time()
        with open("z_out.xml", "wb") as f:
            f.write(etree.tostring(population[-1]["solution"].process))
            print(population[-1]["solution"].invalid_branches)


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
            f.write(etree.tostring(population[0]["solution"].solution_ra_pst))
