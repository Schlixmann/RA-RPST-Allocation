from context import src
import unittest
import shutil
from lxml import etree
from src.tree import parser, task_node as tn, gtw_node as gtw
from pptree import *
from PrettyPrint import PrettyPrintTree
from src.allocation.utils import *


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
        res = "resource_config/offer_resources_many_invalid_branches copy.xml"
        out = "resource_config/offer_resources_many_invalid_branches.xml"
        in_de_re_ratios=[0.3, 0.5, 0.1]
        vary_resource_costs(res, "cost", out_path=out, max_val=150)
    
    def test_add_profile(self):
        res = "resource_config/offer_resources_vary.xml"
        out = "testy2.xml"
        add_resources_for_inserts(res, ["dummy"], ["level1", "level2", "level3"], ratio=0.8, output_file=out)
    
    def test_multi_it(self):
        process = "tests/test_processes/offer_process_paper.xml"
        res_org = "resource_config/offer_resources_plain.xml"
        dest = res_org[:-4] + "_fully_synthetic_small.xml"
        shutil.copyfile(res_org, dest)
        res = dest
        out = "testy.xml"
        in_de_re_ratios=[0.6, 0.2, 0.1]
        for i in range(4):
            vary_resource_changepatterns(process, res, cp_ratio=0.22, in_de_re_ratios=in_de_re_ratios, tasks= ["data_support", "head_confirmation", "four_eyes_principle", "inform_head", "create_proposal"])
            add_resources_for_inserts(res, ["data_support", "head_confirmation", "four_eyes_principle", "inform_head", "create_proposal"], ["level1", "level2", "level3"], ratio=0.11)
        vary_resource_costs(res, "cost")
    





        