from context import tree_allocation
import unittest
from lxml import etree
from tree_allocation.tree import parser

class TestEvent(unittest.TestCase):
    def test_parser(self):
        with open("main_process.xml") as f:
            process = etree.parse(f)
    
        print("success")
        parser.parse_xml(process)
