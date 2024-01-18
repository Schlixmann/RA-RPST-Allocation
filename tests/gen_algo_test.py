from context import tree_allocation
import unittest
from lxml import etree
from tree_allocation.tree import parser, task_node as tn, gtw_node as gtw
from tree_allocation.allocation import allocation
from pptree import *
from PrettyPrint import PrettyPrintTree

from tree_allocation.allocation.solution_search import Genetic
class TestGenetic(unittest.TestCase):
    def test_genetic_base(self):
        ga = Genetic(10,10,50)
        outcome = ga.find_solution("bla")
        print(outcome)

