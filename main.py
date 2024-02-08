from tree_allocation.allocation.solution_search import Genetic,Brute, combine_pickles
from tree_allocation.allocation.cpee_allocation import *


from lxml import etree
from collections import defaultdict
import time
import json
import sys

def run(process_file_path, resource_file_path, tries=10, brute:bool =False, out_folder="results/experiments"):
    with open(process_file_path) as f: 
        task_xml = f.read()
    with open(resource_file_path) as f:
        resource_et = etree.fromstring(f.read())
    
    process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
    trees = process_allocation.allocate_process()
    
    show = True
    for i, tree in enumerate(list(trees.values())):    
        if i > 0:
            show = False
        graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), format="svg", filename=f"alloc_tree_{i}", view=show) 
    
    """
    # Overall Solutions:
    brute_solutions = Brute(process_allocation)
    solutions, tasklist = brute_solutions.get_all_opts()
    solutions = [list(o.values())[0] for o in solutions]
    num_brute_solutions = brute_solutions.iter_product(solutions)

    # heuristic_approach
    # heuristic config:
    heuristic_config = {"top_n":2, "include_invalid":True, "measure":"cost"}
    start = time.time()
    brute_solutions = Brute(process_allocation)
    brute_solutions.find_solutions_with_heuristic(top_n=2, force_valid=False)
    ProcessAllocation.solutions = brute_solutions.solutions
    outcome = brute_solutions.get_best_solutions(heuristic_config["measure"], 
                                                 include_invalid=heuristic_config["include_invalid"], top_n=10)
    end = time.time()

    performance_heuristic = defaultdict(list)
    performance_heuristic["solver"].append("heuristic")
    performance_heuristic["time"].append(float(end-start))
    performance_heuristic["items"]= [[solution[heuristic_config["measure"]] for solution in outcome]]
    performance_heuristic["best"].append(outcome[-1][heuristic_config["measure"]])

    with open(out_folder + "/heur_results_paper.json", "w") as f:
        json.dump(performance_heuristic, f)
    
    with open(out_folder + "/proc/heuristic.xml", "wb") as f:
        f.write(etree.tostring(outcome[-1]["solution"].process))

    print(outcome)
    print(f"Time: {end-start}")
    
    print("Invalid Branches? ", [ind["solution"].invalid_branches for ind in outcome])


    # TOP 10 Outcome: 
    # List with 10 best processes

    # genetic_approach
    # genetic_config: 
    performance_genetic = defaultdict(list)
    for i in range(tries): 
        print(i)
        genetic_config = {"pop_size":25, "generations":100, "k_sel":3, "k_mut":0.2,"early_abandon":True} # pop_size, generations, k_sel, k_mut, early_abandon
        
        start = time.time()
        genetic_solutions = Genetic(process_allocation, genetic_config["pop_size"], genetic_config["generations"], 
                                    genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
        outcome, data = genetic_solutions.find_solutions("plain", "cost")
        end = time.time()

        
        performance_genetic["solver"].append("plain")
        performance_genetic[f"times"].append(float(end-start))
        performance_genetic[f"bests"].append(genetic_solutions.best_tournament[-1])
        #performance_genetic["fitnesses"] = data["fitnesses"]
        performance_genetic[f"avg_fits"].append(data["avg_fit"])
        performance_genetic[f"min_fits"].append(data["min_fit"])
        performance_genetic[f"max_fits"].append(data["max_fit"])
        performance_genetic[f"items_{i}"] = [[solution[heuristic_config["measure"]] for solution in outcome][-10:]]
        print(f"Time: {end-start}")

    print(outcome) 

    with open(out_folder + "/gen_plain_results_paper.json", "w") as f:
        json.dump(performance_genetic, f)
    with open(out_folder + "/proc/gen_plain.xml", "wb") as f:
        f.write(etree.tostring(outcome[-1]["solution"].process))
    print("Invalid Branches? ", [ind["solution"].invalid_branches for ind in outcome])
    # TOP 10 Outcome: 
    # List with 10 best processes

    # genetic_approach
    # genetic_config: 
    performance_genetic = defaultdict(list)
    for i in range(tries): 
        print(i)
        genetic_config = {"pop_size":25, "generations":100, "k_sel":3, "k_mut":0.2,"early_abandon":True} # pop_size, generations, k_sel, k_mut, early_abandon
        
        start = time.time()
        genetic_solutions = Genetic(process_allocation, genetic_config["pop_size"], genetic_config["generations"], 
                                    genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
        outcome, data = genetic_solutions.find_solutions("elitist", "cost")
        end = time.time()

        
        performance_genetic["solver"].append("elitist")
        performance_genetic[f"times"].append(float(end-start))
        performance_genetic[f"bests"].append(genetic_solutions.best_tournament[-1])
        #performance_genetic["fitnesses"] = data["fitnesses"]
        performance_genetic[f"avg_fits"].append(data["avg_fit"])
        performance_genetic[f"min_fits"].append(data["min_fit"])
        performance_genetic[f"max_fits"].append(data["max_fit"])
        performance_genetic[f"items_{i}"] = [[solution[heuristic_config["measure"]] for solution in outcome][-10:]]
        print(f"Time: {end-start}")

    print(outcome)

    with open(out_folder + "/gen_elite_results_paper.json", "w") as f:
        json.dump(performance_genetic, f)
    with open(out_folder + "/proc/elite.xml", "wb") as f:
        f.write(etree.tostring(outcome[-1]["solution"].process))
    print("Invalid Branches? ", [ind["solution"].invalid_branches for ind in outcome])
    

    # Top 10 Outcomes with Brute Force
    # List with top 10 outcome

    """
    #print("Solution space size: ", num_brute_solutions)
    if brute:
        measure = "cost"
        start = time.time()
        brute_solutions = Brute(process_allocation)
        solutions, tasklist = brute_solutions.get_all_opts()
        solutions = [list(o.values())[0] for o in solutions]
        b = brute_solutions.iter_product(solutions)
        results = brute_solutions.find_solutions_ab(b, measure)
        outcome = combine_pickles()
        end = time.time()
        print(outcome)

        performance_brute = defaultdict(list)
        performance_brute["solver"].append("brute")
        performance_brute["time"].append(float(end-start))
        performance_brute["items"]= [[solution[measure] for solution in outcome]]
        performance_brute["best"].append(outcome[-1][measure])


        with open(out_folder + "/brute_results_paper.json", "w") as f:
            json.dump(performance_brute, f)
        with open(out_folder + "/proc/brute.xml", "wb") as f:
            f.write(outcome[-1]["solution"].process)

        print(f"Time: {end-start}")
        print("Invalid Branches? ", [ind["solution"].invalid_branches for ind in outcome])


    print(f"done with : {resource_file_path}")

if __name__ == "__main__":
    process = "tests/test_processes/offer_process_paper.xml"
    resource = "/home/felixs/Programming_Projects/RDPM_private/resource_config/offer_resources_heterogen.xml" # can we do it without valids?
    out_folder = "results/experiments/heterogen"

    # short process:
    #process = "resource_config/offer_resources_cascade_del.xml"
    #resource = "tests/test_processes/offer_process_short.xml"
    run(process, resource, tries=10, brute=True, out_folder=out_folder)

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