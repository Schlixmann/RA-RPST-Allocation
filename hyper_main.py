from tree_allocation.allocation.solution_search import Genetic,Brute, combine_pickles
from tree_allocation.allocation.cpee_allocation import *


from lxml import etree
from collections import defaultdict
import time
import json
import sys

def run(process_file_path, resource_file_path):
    with open(process_file_path) as f: 
        task_xml = f.read()
    with open(resource_file_path) as f:
        resource_et = etree.fromstring(f.read())
    print("run")
    process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
    process_allocation.allocate_process()

    # TOP 10 Outcome: 
    # List with 10 best processes

    # genetic_approach
    # genetic_config: 
    for i in range(10):
        genetic_config = {"pop_size":25, "generations":100, "k_sel":3, "k_mut":0.2,"early_abandon":True} # pop_size, generations, k_sel, k_mut, early_abandon
        
        start = time.time()
        genetic_solutions = Genetic(process_allocation, genetic_config["pop_size"], genetic_config["generations"], 
                                    genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
        outcome, data = genetic_solutions.find_solutions("elitist", "cost")
        end = time.time()

        performance_genetic = defaultdict(list)
        performance_genetic["solver"].append("elitist")
        performance_genetic["time"].append(float(end-start))
        performance_genetic["best"].append(genetic_solutions.best_tournament[-1])
        performance_genetic["fitnesses"] = data["fitnesses"]
        performance_genetic["avg_fit"] = data["avg_fit"]
        performance_genetic["min_fit"] = data["min_fit"]
        performance_genetic["max_fit"] = data["max_fit"]
        performance_genetic["items"] = [[solution[genetic_config["measure"]] for solution in outcome][-10:]]

    # Top 10 Outcomes: 
    # List with top 10 outcomes
    print(outcome) 
    with open("results/gen_results_paper.json", "w") as f:
        json.dump(performance_genetic, f)


if __name__ == "__main__":
    process = "tests/test_processes/offer_process_paper.xml"
    resource = "resource_config/offer_resources_heterogen.xml"

    # short process:
    #process = "resource_config/offer_resources_cascade_del.xml"
    #resource = "tests/test_processes/offer_process_short.xml"
    run(process, resource)

    i = None
    if i:
        print ('argument list', sys.argv)
        process = int(sys.argv[1])
        resource = int(sys.argv[2])
        plot = int(sys.argv[3])
        #print ("sum = {}".format(first+second))

# TODO dienstag: 
    # Hyperparametertuning --> Measure in one Graph
    # Different Branch numbers for Heuristic --> Show in one graph
    # 
    # Develop other use cases for testing Heuristic & GA
    # --> Develop use cases only with different resource settings