from src.allocation.reinforcement_solution import DQNAgentConfiguration
from src.allocation.cpee_allocation import ProcessAllocation
from src.allocation.reinforcement_solution import JobShopEnv
from src.tree.graphix import TreeGraph


import numpy as np
from lxml import etree
import copy
from collections import defaultdict
import pickle

def train_dqn(env, episodes=1000, batch_size=32):
    state_size = env.get_state_aggregation().shape[0]
    max_action_size = len(env.get_possible_branches()[1]) # All branches in RA-PST are possible actions
    agent = DQNAgentConfiguration(state_size, max_action_size)
    
    for e in range(episodes):
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        
        while True:
            possible_actions = env.get_possible_actions()
            action = agent.act(state, possible_actions)
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            
            if done:
                print(f"Episode: {e}/{episodes}, score: {reward}, e: {agent.epsilon:.2}")
                
                with open("final.xml", "wb") as f:
                    f.write(etree.tostring(env.solution.process))
                print(f"Is invalid? {env.solution.invalid_branches}, TPT: {env.last_task_end}")
                break
                
            if len(agent.memory) > batch_size:
                agent.replay(batch_size)
    
    return agent

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

with open("schedule.pkl", "rb") as f:
    new = pickle.load(f)
schedule = defaultdict(list)        

env = JobShopEnv(process, new)

agent = train_dqn(env)