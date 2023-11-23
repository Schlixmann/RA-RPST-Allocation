from context import tree_allocation
import unittest
from lxml import etree
from tree_allocation.tree import parser, task_node as tn, gtw_node as gtw
from pptree import *
from PrettyPrint import PrettyPrintTree


class TestEvent(unittest.TestCase):
    def test_parser(self):
        with open("main_process.xml") as f:
            process = etree.parse(f)
    
        print("success")
        tree = parser.parse_xml(process)
        print(tree)
        pt = PrettyPrintTree(lambda x: x.children, lambda x: "task:" + str(x.label) if type(x) == tn.TaskNode or type(x) == gtw.GtwNode else "GTW:" + str(x))
        pt(tree)