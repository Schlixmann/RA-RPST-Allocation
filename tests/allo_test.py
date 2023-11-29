from context import tree_allocation
import unittest
from lxml import etree
from tree_allocation.tree import parser, task_node as tn, gtw_node as gtw
from tree_allocation.allocation import allocation
from pptree import *
from PrettyPrint import PrettyPrintTree

class TestAllocation(unittest.TestCase):
    def test_allo_creation(self):
        task_xml = """
        
        <call id="a6" endpoint="" xmlns="http://cpee.org/ns/description/1.0">
            <parameters>
                <label>Deepclean</label>
                <method>:post</method>
                <arguments/>
            </parameters>
            <annotations>
                <_timing>
                <_timing_weight/>
                <_timing_avg/>
                <explanations/>
                </_timing>
                <_shifting>
                <_shifting_type>Duration</_shifting_type>
                </_shifting>
                <_context_data_analysis>
                <probes/>
                <ips/>
                </_context_data_analysis>
                <report>
                <url/>
                </report>
                <_notes>
                <_notes_general/>
                </_notes>
            </annotations>
            <documentation>
                <input/>
                <output/>
                <implementation>
                <description/>
                </implementation>
            </documentation>
            <resources allocated_to="not_allocated">
                <resource>Worker</resource>
            </resources>
            </call>
        
        """

        task_node = tn.TaskNode.fromrawxml(task_xml)
        test_allo = allocation.TaskAllocation(task_node)
        print("Test_allo:", test_allo.task.label)
        self.assertEqual(test_allo.state, "initialized")

    def test_1task_allo(self):
        task_xml = """
            <call id="a6" endpoint="" xmlns="http://cpee.org/ns/description/1.0">
            <parameters>
                <label>Drill Hole into product</label>
                <method>:post</method>
                <arguments/>
            </parameters>
            <annotations>
                <_timing>
                <_timing_weight/>
                <_timing_avg/>
                <explanations/>
                </_timing>
                <_shifting>
                <_shifting_type>Duration</_shifting_type>
                </_shifting>
                <_context_data_analysis>
                <probes/>
                <ips/>
                </_context_data_analysis>
                <report>
                <url/>
                </report>
                <_notes>
                <_notes_general/>
                </_notes>
            </annotations>
            <documentation>
                <input/>
                <output/>
                <implementation>
                <description/>
                </implementation>
            </documentation>
            <resources allocated_to="not_allocated">
                <resource>Drill</resource>
            </resources>
            </call>
        
        """

        task_node = tn.TaskNode.fromrawxml(task_xml)
        test_allo = allocation.TaskAllocation(task_node)

        with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/drill.xml") as f: 
            resource_et = etree.fromstring(f.read())
        
        test_allo.allocate_task(resource_url=resource_et)
        tree = test_allo.intermediate_trees[0]
        print(tree)
        pt = PrettyPrintTree(lambda x: x.children, lambda x: "task:" + str(x.label) if type(x) == tn.TaskNode or type(x) == gtw.GtwNode else "RP:" + str(x.name) + " Res: " + str(x.resource.name))
        pt(tree)

