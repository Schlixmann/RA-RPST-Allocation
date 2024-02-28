from src.allocation.solution_search import Genetic,Brute, combine_pickles
from src.allocation.cpee_allocation import *


from lxml import etree
from collections import defaultdict
import time
import json
import sys
import tqdm
import os

def run_pops(process_file_path, resource_file_path, folder_path= "results/hyper/pops"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
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
    findings = []
    for i in range(10):
        genetic_config = {"pop_size":10*(i+1), "generations":75, "k_sel":3, "k_mut":0.2,"early_abandon":True} # pop_size, generations, k_sel, k_mut, early_abandon
        

        genetic_solutions = Genetic(process_allocation, genetic_config["pop_size"], genetic_config["generations"], 
                                    genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
        findings.append(defaultdict(list))
        start = time.time()
        population, data = genetic_solutions.find_solutions("elitist", "cost")
        end = time.time()
        gen_time = end - start
        findings[i]["solver"].append(f"elitist_{i}")
        findings[i]["time"].append(gen_time)
        findings[i]["best"].append(genetic_solutions.best_tournament[-1])
        findings[i]["fitnesses"] = data["fitnesses"]
        findings[i]["avg_fit"] = data["avg_fit"]
        findings[i]["min_fit"] = data["min_fit"]
        findings[i]["max_fit"] = data["max_fit"]
        findings[i]["no_unique_solutions"] = data["unique_solutions"]
        findings[i]["generations"] = genetic_config["generations"]
        findings[i]["pops_size"] = genetic_config["pop_size"]
        with open(folder_path + f"/findings_{i}.json", "w") as f:
            json.dump(findings[i], f)

def run_gens(process_file_path, resource_file_path, folder_path= "results/hyper/gens"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
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
    findings = []
    for i in range(10):
        genetic_config = {"pop_size":12, "generations":25*(i+1), "k_sel":3, "k_mut":0.2,"early_abandon":True} # pop_size, generations, k_sel, k_mut, early_abandon
        

        genetic_solutions = Genetic(process_allocation, genetic_config["pop_size"], genetic_config["generations"], 
                                    genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
        findings.append(defaultdict(list))
        start = time.time()
        population, data = genetic_solutions.find_solutions("elitist", "cost")
        end = time.time()
        gen_time = end - start
        findings[i]["solver"].append(f"elitist_{i}")
        findings[i]["time"].append(gen_time)
        findings[i]["best"].append(genetic_solutions.best_tournament[-1])
        findings[i]["fitnesses"] = data["fitnesses"]
        findings[i]["avg_fit"] = data["avg_fit"]
        findings[i]["min_fit"] = data["min_fit"]
        findings[i]["max_fit"] = data["max_fit"]
        findings[i]["generations"] = genetic_config["generations"]
        findings[i]["gens_size"] = genetic_config["generations"]
        findings[i]["no_unique_solutions"] = data["unique_solutions"]
        findings[i]["gens"] = genetic_config["generations"]
        with open(folder_path + f"/findings_{i}.json", "w") as f:
            json.dump(findings[i], f)

def run_mut(process_file_path, resource_file_path, folder_path= "results/hyper/mut"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
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
    findings = []
    for i in range(10):
        genetic_config = {"pop_size":12, "generations":75, "k_sel":2, "k_mut":0.1*(i+1),"early_abandon":True} # pop_size, generations, k_sel, k_mut, early_abandon
        

        genetic_solutions = Genetic(process_allocation, genetic_config["pop_size"], genetic_config["generations"], 
                                    genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
        findings.append(defaultdict(list))
        start = time.time()
        population, data = genetic_solutions.find_solutions("elitist", "cost")
        end = time.time()
        gen_time = end - start
        findings[i]["solver"].append(f"elitist_{i}")
        findings[i]["time"].append(gen_time)
        findings[i]["best"].append(genetic_solutions.best_tournament[-1])
        findings[i]["fitnesses"] = data["fitnesses"]
        findings[i]["avg_fit"] = data["avg_fit"]
        findings[i]["min_fit"] = data["min_fit"]
        findings[i]["max_fit"] = data["max_fit"]
        findings[i]["no_unique_solutions"] = data["unique_solutions"]
        findings[i]["generations"] = genetic_config["generations"]
        findings[i]["mut_size"] = genetic_config["k_mut"]
        with open(folder_path + f"/findings_{i}.json", "w") as f:
            json.dump(findings[i], f)

def run_sel(process_file_path, resource_file_path, folder_path= "results/hyper/sel"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
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
    findings = []
    for i in range(10):
        print(2+i)
        genetic_config = {"pop_size":12, "generations":75, "k_sel":2+i, "k_mut":0.2,"early_abandon":False} # pop_size, generations, k_sel, k_mut, early_abandon
        

        genetic_solutions = Genetic(process_allocation, genetic_config["pop_size"], genetic_config["generations"], 
                                    genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
        findings.append(defaultdict(list))
        start = time.time()
        population, data = genetic_solutions.find_solutions("elitist", "cost")
        end = time.time()
        gen_time = end - start
        findings[i]["solver"].append(f"elitist_{i}")
        findings[i]["time"].append(gen_time)
        findings[i]["best"].append(genetic_solutions.best_tournament[-1])
        findings[i]["fitnesses"] = data["fitnesses"]
        findings[i]["avg_fit"] = data["avg_fit"]
        findings[i]["min_fit"] = data["min_fit"]
        findings[i]["max_fit"] = data["max_fit"]
        findings[i]["no_unique_solutions"] = data["unique_solutions"]
        with open(folder_path + f"/findings_{i}.json", "w") as f:
            json.dump(findings[i], f)

def run_all(process_file_path, resource_file_path):
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
    findings = []
    for i in tqdm.tqdm(range(10)):
        for j in tqdm.tqdm(range(10)):
            for k in tqdm.tqdm(range(10)):
                genetic_config = {"pop_size":12*(i+1), "generations":18*(j+1), "k_sel":3, "k_mut":0.1*(k+1),"early_abandon":False} # pop_size, generations, k_sel, k_mut, early_abandon
                genetic_solutions = Genetic(process_allocation, genetic_config["pop_size"], genetic_config["generations"], 
                                            genetic_config["k_sel"], genetic_config["k_mut"], genetic_config["early_abandon"])
                findings.append(defaultdict(list))
                start = time.time()
                population, data = genetic_solutions.find_solutions("elitist", "cost")
                end = time.time()
                gen_time = end - start
                findings[i]["solver"].append(f"elitist_{i}")
                findings[i]["time"].append(gen_time)
                findings[i]["best"].append(genetic_solutions.best_tournament[-1])
                findings[i]["fitnesses"] = data["fitnesses"]
                findings[i]["avg_fit"] = data["avg_fit"]
                findings[i]["min_fit"] = data["min_fit"]
                findings[i]["max_fit"] = data["max_fit"]
                findings[i]["no_unique_solutions"] = data["unique_solutions"]
                with open(f"results/hyper/all/findings_{i}_{j}_{k}.json", "w") as f:
                    json.dump(findings[i], f)

if __name__ == "__main__":
    process = "tests/test_processes/offer_process_paper.xml"
    resource = "resource_config/offer_resources_heterogen.xml"

    # short process:
    #process = "resource_config/offer_resources_cascade_del.xml"
    #resource = "tests/test_processes/offer_process_short.xml"
    run_pops(process, resource, folder_path="results/hyper/pops/abandon")
    run_gens(process, resource, folder_path="results/hyper/gens/abandon")
    run_mut(process, resource, folder_path="results/hyper/mut/abandon")
    #run_sel(process, resource)
    #run_all(process, resource)
    #TODO run without different gen sizes and with abandoning
    print("done")
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