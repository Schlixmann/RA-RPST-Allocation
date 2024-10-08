from src.allocation.solution_search import Genetic,Brute, combine_pickles
from src.allocation.cpee_allocation import *


from lxml import etree
from collections import defaultdict
import argparse
import time
import json
import sys


# TODO: Fix main to new solution search process


def run(process_file_path, resource_file_path, tries=10, brute:bool =False, out_folder="results/experiments"):
    with open(process_file_path) as f: 
        task_xml = f.read()
    with open(resource_file_path) as f:
        resource_et = etree.fromstring(f.read())
    
    process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
    process_allocation.allocate_process()    

    # Overall Solutions:
    process_allocation.solver = Brute(process_allocation.ra_rpst)
    solutions, tasklist = process_allocation.solver.get_all_opts()
    solutions = [list(o.values())[0] for o in solutions]
    num_brute_solutions = process_allocation.solver.iter_product(solutions)

        #print("Solution space size: ", num_brute_solutions)
    if brute:
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

    # heuristic_approach
    # heuristic config:
    heuristic_config = {"top_n":2, "include_invalid":False, "measure":"cost"}

    process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
    process_allocation.allocate_process()
    process_allocation.solver = Brute(process_allocation.ra_rpst)

    start = time.time()
    solutions = process_allocation.solver.find_solutions_with_heuristic(measure="cost", top_n=1, force_valid=True)
    
    outcome = process_allocation.solver.get_best_solutions(heuristic_config["measure"], 
                                                 include_invalid=heuristic_config["include_invalid"], top_n=10)
    end = time.time()

    performance_heuristic = defaultdict(list)
    performance_heuristic["solver"].append("heuristic")
    performance_heuristic["size"].append(len(num_brute_solutions))
    performance_heuristic["time"].append(float(end-start))
    performance_heuristic["items"]= [[solution[heuristic_config["measure"]] for solution in outcome]]
    performance_heuristic["best"].append(outcome[-1][heuristic_config["measure"]])

    with open(out_folder + "/heur_results_paper.json", "w") as f:
        json.dump(performance_heuristic, f)
    
    with open(out_folder + "/proc/heuristic.xml", "wb") as f:
        f.write(etree.tostring(outcome[-1]["solution"].solution_ra_pst))

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
        
        process_allocation.solver = Genetic(process_allocation.ra_rpst, genetic_config["pop_size"], genetic_config["generations"], 
                                    genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
        start = time.time()
        outcome, data = process_allocation.solver.find_solutions("plain", "cost")
        end = time.time()

        
        performance_genetic["solver"].append("plain")
        performance_genetic["size"].append(len(num_brute_solutions))
        performance_genetic[f"times"].append(float(end-start))
        performance_genetic[f"bests"].append(process_allocation.solver.best_tournament[-1])
        #performance_genetic["fitnesses"] = data["fitnesses"]
        performance_genetic[f"avg_fits"].append(data["avg_fit"])
        performance_genetic[f"min_fits"].append(data["min_fit"])
        performance_genetic[f"max_fits"].append(data["max_fit"])
        performance_genetic[f"items_{i}"] = [[solution[heuristic_config["measure"]] for solution in filter(lambda x: not x["solution"].invalid_branches, outcome)][-10:]]
        performance_genetic["best_final"].append(min(performance_genetic[f"items_{i}"][0]))
        print(f"Time: {end-start}")

    print(outcome) 

    with open(out_folder + "/gen_plain_results_paper.json", "w") as f:
        json.dump(performance_genetic, f)
    with open(out_folder + "/proc/gen_plain.xml", "wb") as f:
        f.write(etree.tostring(outcome[-1]["solution"].solution_ra_pst))
    print("Invalid Branches? ", [ind["solution"].invalid_branches for ind in outcome])
    # TOP 10 Outcome: 
    # List with 10 best processes
    
    
    # genetic_approach
    # genetic_config: 
    performance_genetic = defaultdict(list)
    for i in range(tries): 
        print(i)
        genetic_config = {"pop_size":25, "generations":100, "k_sel":3, "k_mut":0.2,"early_abandon":True} # pop_size, generations, k_sel, k_mut, early_abandon
        
        process_allocation.solver = Genetic(process_allocation.ra_rpst, genetic_config["pop_size"], genetic_config["generations"], 
                                    genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
        start = time.time()
        outcome, data = process_allocation.solver.find_solutions("elitist", "cost")
        end = time.time()

        
        performance_genetic["solver"].append("elitist")
        performance_genetic["size"].append(len(num_brute_solutions))
        performance_genetic[f"times"].append(float(end-start))
        performance_genetic[f"bests"].append(process_allocation.solver.best_tournament[-1])
        #performance_genetic["fitnesses"] = data["fitnesses"]
        performance_genetic[f"avg_fits"].append(data["avg_fit"])
        performance_genetic[f"min_fits"].append(data["min_fit"])
        performance_genetic[f"max_fits"].append(data["max_fit"])
        performance_genetic[f"items_{i}"] = [[solution[heuristic_config["measure"]] for solution in filter(lambda x: not x["solution"].invalid_branches, outcome)][-10:]]
        performance_genetic["best_final"].append(min(list(performance_genetic[f"items_{i}"][0])))
        print(f"Time: {end-start}")

    print(outcome)

    with open(out_folder + "/gen_elite_results_paper.json", "w") as f:
        json.dump(performance_genetic, f)
    with open(out_folder + "/proc/elite.xml", "wb") as f:
        f.write(etree.tostring(outcome[-1]["solution"].solution_ra_pst))
    print("Invalid Branches? ", [ind["solution"].invalid_branches for ind in outcome])

    # Top 10 Outcomes with Brute Force
    # List with top 10 outcome
    
    print(f"done with : {resource_file_path}")

if __name__ == "__main__":
    process = "processes/offer_process_paper.xml"

    parser = argparse.ArgumentParser(description="""Run all experiments as described in the paper with this function. \n
                                     To force the calculation of all solutions: use -b (be aware of long execution times) \n
                                     You can access the results by running 'results_presentation/results.ipynb' """)
    parser.add_argument("-b", "--brute", action="store_true", help="Enable brute-force mode, default == False")

    args = parser.parse_args()


    targets = {"resource_config/offer_resources_heterogen.xml" : "results/experiments/heterogen",
        "resource_config/offer_resources_close_maxima.xml" : "results/experiments/close_maxima",
        "resource_config/offer_resources_many_invalid_branches.xml" : "results/experiments/invalid_branches",
        "resource_config/offer_resources_heterogen_no_deletes.xml" : "results/experiments/no_deletes",
        "resource_config/offer_resources_plain_fully_synthetic_small.xml" : "results/experiments/fully_synthetic",
        }
    
    for resource, target in targets.items():
        run(process, resource, 10, args.brute, target)
        