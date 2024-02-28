from context import src
import unittest
from lxml import etree
from src.tree import parser, task_node as tn, gtw_node as gtw, res_node as rn
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
        
        new_task = tn.TaskNode.fromrawxml(xml_str)
        print("new_task", new_task.task_id)
        self.assertEqual([new_task.task_id, new_task.label, new_task.allowed_roles ], ["a5", "Normal Measure", ["Worker"]])
        
        
        et_str = etree.fromstring(xml_str)
        print(type(et_str))
        second_task = tn.TaskNode.frometree(et_str)
        print("second_task", second_task.task_id)
        self.assertEqual([second_task.task_id, second_task.label, second_task.allowed_roles ], ["a5", "Normal Measure", ["Worker"]])


    def test_res_node(self):
        xml_str = """

            <resource id="1" name="Good Drill" activeRole="">
                <resprofile id="11" name="autodrill" role ="Drill" task="Drill Hole into product"> <!--{{{-->
                    <measures>
                        <cost>50</cost>
                        <time>10</time>
                    </measures>
                    <changepattern type="insert">
                        <parameters>
                            <direction>before</direction>
                        </parameters>
                        <description xmlns="http://cpee.org/ns/description/1.0">
                            <manipulate id="r1" label="Setup Drill">
                                <resources allocated_to="not_allocated">
                                    <resource>Technician</resource>
                                </resources>
                            </manipulate>
                        </description>
                    </changepattern>
                </resprofile>
                        <resprofile id="22" name="manual drill" role ="Drill" task="drill hole into product"> <!--{{{-->
                    <measures>
                        <cost>10</cost>
                        <time>30</time>
                    </measures>
                </resprofile>
            </resource>

        """
        #resnode = rn.ResourceNode()
        new_res = rn.ResourceNode.fromrawxml(xml_str=xml_str)
        print(new_res.resource_profiles)