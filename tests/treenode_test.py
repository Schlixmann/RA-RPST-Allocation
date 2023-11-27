from context import tree_allocation
import unittest
from lxml import etree
from tree_allocation.tree import parser, task_node as tn, gtw_node as gtw
from pptree import *
from PrettyPrint import PrettyPrintTree


class TestTreeNode(unittest.TestCase):
    def test_task_node(self):
        xml_str = """
        <call id="a5" endpoint="Test_Endpoint" xmlns="http://cpee.org/ns/description/1.0">
            <parameters>
                <label>Normal Measure</label>
                <method>:post</method>
                <arguments/>
            </parameters>
            <annotations>
                <_timing>
                ...
                </_timing>
                <_shifting>
                ...
                </_shifting>
                <_context_data_analysis>
                ...
                </_context_data_analysis>
                <report>
                ...
                </report>
                <_notes>
                ...
                </_notes>
            </annotations>
            <documentation>
            ...
            </documentation>
            <resources allocated_to="not_allocated">
                <resource>Worker</resource>
            </resources>
        </call>
        """
        tasknode = tn.TaskNode()
        new_task = tasknode.fromrawxml(xml_str)
        print("new_task", new_task.task_id)
        self.assertEqual([new_task.task_id, new_task.label, new_task.allowed_roles ], ["a5", "Normal Measure", ["Worker"]])
        
        tasknode = tn.TaskNode()
        et_str = etree.fromstring(xml_str)
        print(type(et_str))
        second_task = tasknode.frometree(et_str)
        print("second_task", second_task.task_id)
        self.assertEqual([second_task.task_id, second_task.label, second_task.allowed_roles ], ["a5", "Normal Measure", ["Worker"]])

