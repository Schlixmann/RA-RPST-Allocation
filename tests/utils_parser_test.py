from context import tree_allocation
import unittest
from lxml import etree
from tree_allocation.tree import parser, task_node as tn, gtw_node as gtw
from pptree import *
from PrettyPrint import PrettyPrintTree
from tree_allocation.allocation.utils import *


class TestEvent(unittest.TestCase):
    def test_parser(self):
        with open("main_process.xml") as f:
            process = etree.parse(f)
    
        print("success")
        tree = parser.parse_xml(process)
        print(tree)
        pt = PrettyPrintTree(lambda x: x.children, lambda x: "task:" + str(x.label) if type(x) == tn.TaskNode or type(x) == gtw.GtwNode else "GTW:" + str(x))
        pt(tree)

    def test_int_proc(self):
        with open("main_process.xml") as f:
            process = f.read()
        
        tree = parser.internal_process_parser(process)
        print(tree)
        print("children: ", tree.xpath("//*"))

    def test_vary_cp(self):
        process = "tests/test_processes/offer_process_paper.xml"
        res = "resource_config/offer_resources_heterogen.xml"
        out = "testy.xml"
        in_de_re_ratios=[0.5, 0.4, 0.1]
        vary_resource_changepatterns(process, res, out, cp_ratio=0.4, in_de_re_ratios=in_de_re_ratios)


    def test_vary_res(self):
        res = "resource_config/offer_resources_heterogen.xml"
        out = "testy.xml"
        in_de_re_ratios=[0.5, 0.4, 0.1]
        vary_resource_costs(res, "cost")


        