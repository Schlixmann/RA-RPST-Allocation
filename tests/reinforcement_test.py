import unittest
from lxml import etree
import copy
from collections import defaultdict
import pickle

from src.allocation.cpee_allocation import ProcessAllocation
from src.allocation.reinforcement_solution import JobShopEnv
from src.allocation.solution import Solution
from src.tree.graphix import TreeGraph

class TestReinforcementApproach(unittest.TestCase):

    def test_build_ra_rpst(self):        
        with open("tests/test_processes/offer_process_paper.xml") as f: 
            task_xml = f.read()
        with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/offer_resources_many_invalid_branches.xml") as f:
            resource_et = etree.fromstring(f.read())
        
        # Create RA-PST
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
        trees = process_allocation.allocate_process()
        ra_rpst = process_allocation.get_ra_rpst()

        # Create JobShopEnv
        with open("RA-PST.xml", "wb") as f:
            f.write(ra_rpst)
        with open("trees.xml", "wb") as f:
            f.write(etree.tostring(process_allocation.process))

        ra_pst2 = copy.deepcopy(ra_rpst)
        processes = [ra_rpst, ra_pst2]


        i = 0
        schedule = defaultdict(dict)
        ns = {"cpee1": list(etree.fromstring(ra_rpst).nsmap.values())[0]}

        for instance in processes:
            env = JobShopEnv(instance, schedule=schedule, current_instance_id=i)
            done = False
            while not done :
                state, reward, done, _ = env.step()
            env.sort_schedule_by_resource()
            schedule = env.schedule
            print("Schedule", schedule)
            print(env.valid_solution)
        
            with open("final_config.xml", "wb") as f:
                f.write(etree.tostring(env.final_config))
            i += 1

        with open("schedule.pkl", "wb") as f:
            pickle.dump(env.schedule, f)
        print(env.get_state())
    
    def test_get_possible_branches(self):        
        with open("tests/test_processes/offer_process_paper.xml") as f: 
            task_xml = f.read()
        with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/offer_resources_many_invalid_branches.xml") as f:
            resource_et = etree.fromstring(f.read())
        
        # Create RA-PST
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
        trees = process_allocation.allocate_process()
        ra_rpst = process_allocation.get_ra_rpst()

        # Create JobShopEnv
        with open("RA-PST.xml", "wb") as f:
            f.write(ra_rpst)
        with open("trees.xml", "wb") as f:
            f.write(etree.tostring(process_allocation.process))

        ra_pst2 = copy.deepcopy((ra_rpst))
        process = ra_rpst

        with open("schedule.pkl", "rb") as f:
            new = pickle.load(f)
        schedule = defaultdict(list)        

        env = JobShopEnv(process, new)
        all_possible_branches, max_branches = env.get_possible_branches()
        print(all_possible_branches, max_branches)
        a = env.get_state_aggregation()
        print(a)
    
    def test_random_schedule(self): 

        # Train the DQN agent
        with open("tests/test_processes/offer_process_sequential.xml") as f: 
                    task_xml = f.read()
        with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/offer_resources_many_invalid_branches_sequential.xml") as f:
            resource_et = etree.fromstring(f.read())

        # Create RA-PST
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
        trees = process_allocation.allocate_process()
        ra_rpst = Solution(process_allocation.get_ra_rpst()).transform_to_valid_only_ra_pst().solution_ra_pst


        ra_pst2 = copy.deepcopy((ra_rpst))
        process = ra_rpst

        with open("schedule.pkl", "rb") as f:
            new = pickle.load(f)
        schedule = defaultdict(list)

        env = JobShopEnv(process, new)
        env.create_random_schedule()



