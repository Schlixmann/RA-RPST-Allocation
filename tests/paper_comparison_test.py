import unittest
from lxml import etree
from pptree import *
import time
import random
from collections import defaultdict
import json
import numpy as np

from src.allocation.solution_search import Genetic,Brute
from src.allocation import cpee_allocation
from src.tree import parser, task_node as tn, gtw_node as gtw
from src.allocation import gen_deap

class TestGenetic(unittest.TestCase):
    
    
    def test_gen_vs_brute_short(self):
        with open("resource_config/offer_resources_close_maxima.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_paper.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = ProcessAllocation.allocate_process()

        findings = []
        i = 0
        findings.append(defaultdict(list))
        start = time.time()
        genetic_solutions = Genetic(ProcessAllocation, pop_size=25, generations=25, k_mut=0.2)
        population, data = genetic_solutions.find_solutions("elitist", "cost", early_abandon=True)
        end = time.time()
        gen_time = end - start
        findings[i]["solver"].append("elitist")
        findings[i]["time"].append(gen_time)
        findings[i]["best"].append(genetic_solutions.best_tournament[-1])
        findings[i]["fitnesses"] = data["fitnesses"]
        findings[i]["avg_fit"] = data["avg_fit"]
        findings[i]["min_fit"] = data["min_fit"]
        findings[i]["max_fit"] = data["max_fit"]
        with open(f"findings_{i}.json", "w") as f:
            json_object = json.dumps(findings[i], indent=4)
            f.write(json_object)
        solutions = [solution["solution"] for solution in population]
        gen_best_solution = solutions[np.argmin([solution["solution"].get_measure("cost") for solution in population])]
        
        
        start = time.time()
        brute_solutions = Brute(ProcessAllocation)
        brute_solutions.find_solutions_with_heuristic(top_n=2)
        ProcessAllocation.solutions = brute_solutions.solutions
        heur_best_solutions = brute_solutions.get_best_solutions("cost", include_invalid=False, top_n=5)
        end = time.time()
        brute_time = end - start
        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(gen_best_solution.process))
        

        heur_best_solution = heur_best_solutions[np.argmin([list(solution.values())[0]for solution in heur_best_solutions ])]
        with open(f"tests/solutions/heur_solution.xml", "wb") as f:
            f.write(etree.tostring(list(heur_best_solution.keys())[0].process))
        
        print(f"Best solutions: \n Genetic : {gen_best_solution.get_measure("cost")}, \n Heuristic: {list(heur_best_solution.values())[0]}")



    def test_approaches(self):
        with open("resource_config/offer_resources.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        ProcessAllocation.allocate_process()

        findings = []
        solv_types = ["plain", "random", "randomparent", "parent", "elitist"]
        #solv_types = ["elitist"]
        for i, stype in enumerate(solv_types):
            
            findings.append(defaultdict(list))
            start = time.time()
            genetic_solutions = Genetic(ProcessAllocation, pop_size=25, generations=25, k_mut=0.2)
            population, data = genetic_solutions.find_solutions(stype, "cost")
            end = time.time()
            gen_time = end - start
            findings[i]["solver"].append(stype)
            findings[i]["time"].append(gen_time)
            findings[i]["best"].append(genetic_solutions.best_tournament[-1])
            findings[i]["fitnesses"] = data["fitnesses"]
            findings[i]["avg_fit"] = data["avg_fit"]
            findings[i]["min_fit"] = data["min_fit"]
            findings[i]["max_fit"] = data["max_fit"]
            with open(f"findings_{i}.json", "w") as f:
                json_object = json.dumps(findings[i], indent=4)
                f.write(json_object)


            
            print(f"{stype} Solutions:")
            for solution in population:
                print("Branches: ", solution["branches"].values())
                print("Solution Costs: ", solution["solution"].get_measure("cost"))
            print("Gen_time: ", gen_time)

        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(population[0]["solution"].process))