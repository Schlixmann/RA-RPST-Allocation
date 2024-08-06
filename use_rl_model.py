from src.allocation.reinforcement_solution import DQNAgentConfiguration
from src.allocation.cpee_allocation import ProcessAllocation
from src.allocation.reinforcement_solution import JobShopEnv
from src.allocation.solution_search import Genetic
from src.allocation.solution import Solution
from src.tree.graphix import TreeGraph


import numpy as np
from lxml import etree
import copy
from collections import defaultdict
import pickle
import json


# Train the DQN agent
with open("tests/test_processes/offer_process_paper.xml") as f: 
            task_xml = f.read()
with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/offer_resources_many_invalid_branches.xml") as f:
    resource_et = etree.fromstring(f.read())

# Create RA-PST
process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
trees = process_allocation.allocate_process()

ra_pst = Solution(process_allocation.get_ra_rpst()).transform_to_valid_only_ra_pst().solution_ra_pst
process_allocation.solver = Genetic(ra_pst, pop_size=25, generations=25, k_mut=0.2)

population, data = process_allocation.solver.find_solutions('elitist', "cost")
genetic_solution = population[-1]['solution']
genetic_solution_ra_pst = genetic_solution.solution_ra_pst

print(process_allocation.solver.best_tournament)

#print(population)
with open("tests/solutions/gen_for_schedule.xml", "wb") as f:
    f.write(etree.tostring(population[-1]["solution"].solution_ra_pst))



with open("used_ra_pst.xml", "wb") as f:
       f.write(etree.tostring(ra_pst))

env = JobShopEnv(ra_pst)


state_size = env.get_state_aggregation().shape[0]
max_action_size = len(env.get_possible_branches()[1])

# Load the trained agent
loaded_agent = DQNAgentConfiguration(state_size, max_action_size)
loaded_agent.load_model("dqn_model.keras", "epsilon.txt")

#env.get_last_scheduled_task_end()
schedule = copy.deepcopy(env.schedule)
comp_schedule = copy.deepcopy(env.schedule)

all_last_tasks= []

for i in range(20):
    state = env.reset()
    env.schedule = copy.deepcopy(schedule)
    state = np.reshape(state, [1, state_size])
    possible_actions = env.get_possible_actions()
    actions = []

    env.current_instance_id=5


    while True:
        print(state, "\n Possible Actions: ", env.get_possible_actions())
        action = loaded_agent.act(state, env.get_possible_actions())
        actions.append(action)
        state, reward, done, _ = env.step(action)
        state = np.reshape(state, [1, state_size])

        if done: 
            break
    print("action:", actions, "Invalid Solution?", env.solution.invalid_branches, "Random Choices: ", loaded_agent.randomness_counter)
    print(f"RL actions: {env.actions}, costs: {env.solution.get_measure("cost")} \n,  Genetic actions: {population[-1]["solution"].allocated_branches}, costs:  {population[-1]["cost"]} ")
    
    all_last_tasks.append(env.get_last_scheduled_task_end())
    
    with open("final.xml", "wb") as f:
        f.write(etree.tostring(env.solution.solution_ra_pst))
                    
    with open("final_schedule.json", "w") as f:
        json.dump(env.schedule, f)

    with open("actions.txt", "a") as f:
        f.write(str(env.actions) + '\n')
    env.solution.check_validity()

gen_al_env = JobShopEnv(genetic_solution_ra_pst, schedule=schedule)
for task in genetic_solution_ra_pst.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=genetic_solution.ns):
    gen_al_env.add_task_to_schedule(task)

with open("final_schedule_gen_al.json", "w") as f:
    json.dump(gen_al_env.schedule, f)
print(f"RL LastTask: {env.get_last_scheduled_task_end()}, Genetic LastTask {gen_al_env.get_last_scheduled_task_end()}")
print(all_last_tasks)
print(sum(num < gen_al_env.get_last_scheduled_task_end() for num in all_last_tasks))