import unittest
from lxml import etree
import copy
from collections import defaultdict

from src.allocation.cpee_allocation import ProcessAllocation
from src.allocation.reinforcement_solution import JobShopEnv

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

        schedule = defaultdict(list)
        
        for instance in processes:
            env = JobShopEnv(instance, schedule)
            done = False
            while not done :
                done, final_process, schedule = env.step()

            with open("final_process.xml", "wb") as f:
                f.write(etree.tostring(final_process))

            print(schedule)
            print(env.valid_solution)
        
            with open("final_config.xml", "wb") as f:
                f.write(etree.tostring(env.final_config))
        print(env.get_state())


