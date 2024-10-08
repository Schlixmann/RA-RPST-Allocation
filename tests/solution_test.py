import unittest
from lxml import etree
import copy
from collections import defaultdict
import pickle

from src.allocation.cpee_allocation import ProcessAllocation
from src.allocation.solution import Solution
from src.allocation.reinforcement_solution import JobShopEnv
from src.tree.graphix import TreeGraph

class TestReinforcementApproach(unittest.TestCase):

    def test_build_ra_rpst(self):        
        with open("tests/test_processes/offer_process_paper.xml") as f: 
            task_xml = f.read()
        with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/offer_resources_many_invalid_branches.xml") as f:
            resource_et = etree.fromstring(f.read())
        
        # Create RA-PST
        process = etree.fromstring(task_xml)
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
        trees = process_allocation.allocate_process()
        ra_rpst = process_allocation.get_ra_rpst()

        solution = Solution(process, process_allocation, ra_rpst)
        print(solution.get_possible_branches())

    def test_transform_to_valid_only_ra_pst(self):
        with open("resource_config/offer_resources_many_invalid_branches.xml") as f: 
            resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_paper.xml") as f:
            task_xml = f.read()
        
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)    
        process_allocation.allocate_process()
        print(type(process_allocation.ra_rpst))
        solution = Solution(etree.fromstring(process_allocation.ra_rpst))

        valid_solution = solution.transform_to_valid_only_ra_pst()

        with open("test.xml", "wb") as f: 
            f.write(etree.tostring(valid_solution.init_ra_pst))
        print("done")       



