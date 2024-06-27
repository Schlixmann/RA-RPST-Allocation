import unittest
from lxml import etree

from src.allocation.cpee_allocation import ProcessAllocation
from src.allocation.reinforcement_solution import JobShopEnv

class TestReinforcementApproach(unittest.TestCase):
    def test_build_ra_rpst(self):        
        with open("tests/test_processes/offer_process_paper.xml") as f: 
            task_xml = f.read()
        with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/offer_resources_heterogen.xml") as f:
            resource_et = etree.fromstring(f.read())
        
        # Create RA-PST
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
        trees = process_allocation.allocate_process()
        ra_rpst = process_allocation.get_ra_rpst()

        # Create JobShopEnv
        env = JobShopEnv(process_allocation.process)
        env.step()


