import unittest
from lxml import etree
from pptree import *
import time
import random
from collections import defaultdict
import json

from tree_allocation.allocation.solution_search import Genetic,Brute
from tree_allocation.allocation import cpee_allocation
from tree_allocation.tree import parser, task_node as tn, gtw_node as gtw
from tree_allocation.allocation import gen_deap

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
        genetic_solutions = Genetic(ProcessAllocation, pop_size=25, generations=10, k_mut=0.50)
        population = genetic_solutions.find_solutions("cost")
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
        with open("resource_config/offer_resources.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_short.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = ProcessAllocation.allocate_process()

        start = time.time()
        genetic_solutions = Genetic(ProcessAllocation, pop_size=30, generations=5,k_sel=3, k_mut=0.1)
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
        
        for i, solution in enumerate(population):
            print(i, ". Branches: ", solution["branches"].values())
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

    def test_deapgen(self):
        with open("resource_config/offer_resources.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_short.xml") as f:
            task_xml = f.read()

        process_allocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        trees = process_allocation.allocate_process()
        gen_obj = gen_deap.DeapGen(process_allocation)
        
        """
        pop = gen_obj.toolbox.population(n=300)
        fitnesses = list(map(gen_obj.toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        CXPB, MUTPB = 0.5, 0.2
        fits = [ind.fitness.values[0] for ind in pop]

            # Variable keeping track of the number of generations
        g = 0

        # Begin the evolution
        while max(fits) < 100 and g < 1000:
            # A new generation
            g = g + 1
            print("-- Generation %i --" % g)

                # Select the next generation individuals
        offspring = gen_obj.toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(gen_obj.toolbox.clone, offspring))

                # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                gen_obj.toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB: 
                gen_obj.toolbox.mutate(mutant)
                del mutant.fitness.values
        
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(gen_obj.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring

                # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)"""


    def test_approaches(self):
        with open("resource_config/offer_resources.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process.xml") as f:
            task_xml = f.read()
        
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)    
        ProcessAllocation.allocate_process()

        findings = []
        solv_types = ["plain", "random", "randomparent", "parent"]
        for i,type in enumerate(solv_types):
            findings.append(defaultdict(list))
            start = time.time()
            genetic_solutions = Genetic(ProcessAllocation, pop_size=25, generations=25, k_mut=0.50)
            population, data = genetic_solutions.solver_factory(type, "cost")
            end = time.time()
            gen_time = end - start
            findings[i]["time"].append(gen_time)
            findings[i]["best"].append(genetic_solutions.best_tournament[-1])
            findings[i]["fitnesses"] = data["fitnesses"]
            findings[i]["avg_fit"] = data["avg_fit"]
            findings[i]["min_fit"] = data["min_fit"]
            findings[i]["max_fit"] = data["max_fit"]
            with open(f"findings_{i}.json", "w") as f:
                json_object = json.dumps(findings[i], indent=4)
                f.write(json_object)


            
        
            for solution in population:
                print("Branches: ", solution["branches"].values())
                print("Solution Costs: ", solution["solution"].get_measure("cost"))
            print("Gen_time: ", gen_time)
            print(genetic_solutions.best_tournament)

        #print(population)
        with open("tests/solutions/gen_solution.xml", "wb") as f:
            f.write(etree.tostring(population[0]["solution"].process))