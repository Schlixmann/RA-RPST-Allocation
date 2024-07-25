from src.allocation.reinforcement_solution import DQNAgentConfiguration
from src.allocation.cpee_allocation import ProcessAllocation
from src.allocation.reinforcement_solution import JobShopEnv
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
ra_rpst = process_allocation.get_ra_rpst()

ra_pst2 = copy.deepcopy((ra_rpst))
process = ra_rpst

with open("used_ra_pst.xml", "wb") as f:
       f.write(ra_rpst)

with open("schedule.pkl", "rb") as f:
    new = pickle.load(f)
schedule = defaultdict(list)        

env = JobShopEnv(process, new)

state_size = env.get_state_aggregation().shape[0]
max_action_size = len(env.get_possible_branches()[1])

# Load the trained agent
loaded_agent = DQNAgentConfiguration(state_size, max_action_size)
loaded_agent.load_model("dqn_model.keras", "epsilon.txt")

state = env.reset()
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

with open("final.xml", "wb") as f:
    f.write(etree.tostring(env.solution.process))
                
with open("final_schedule.json", "w") as f:
    json.dump(env.schedule, f)

with open("actions.txt", "a") as f:
    f.write(str(env.actions) + '\n')
env.solution.check_validity()
print("action:", actions, "Invalid Solution?", env.solution.is_valid, "Random Choices: ", loaded_agent.randomness_counter)