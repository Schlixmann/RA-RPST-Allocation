from context import tree_allocation
import unittest
from lxml import etree
from tree_allocation.tree import parser, task_node as tn, gtw_node as gtw
from tree_allocation.allocation import allocation
from pptree import *
from PrettyPrint import PrettyPrintTree


class TestAllocation(unittest.TestCase):
    def test_allo_creation(self):
        test_allo = allocation.TaskAllocation()
        self.assertEqual(test_allo.state, "finished")

if __name__ == '__main__':
    unittest.main()