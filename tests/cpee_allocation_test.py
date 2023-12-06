from context import tree_allocation
import unittest
from lxml import etree
from tree_allocation.tree import parser, task_node as tn, gtw_node as gtw
from tree_allocation.allocation import cpee_allocation
from pptree import *
from PrettyPrint import PrettyPrintTree
from tree_allocation.tree import graphix


class TestCpeeAllocation(unittest.TestCase):
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
                <allocation>
                </allocation>
                </call>
            
            """

            task_node = task_xml
            
            with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/drill.xml") as f: 
                resource_et = etree.fromstring(f.read())
            
            a = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
            test_allo = cpee_allocation.TaskAllocation(a, task_xml)

            test_allo.allocate_task(resource_url=resource_et)
            
            tree = test_allo.intermediate_trees[0]
            print(tree)
            with open("xml_out.xml", "wb") as f:
                 f.write(etree.tostring(tree))

            graphix.TreeGraph().show(etree.tostring(tree))
            
    def test_1t_process_allo(self):
                task_xml = """
                <description xmlns="http://cpee.org/ns/description/1.0">
                <call id="a6" endpoint="" >
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
                    <allocation>
                    </allocation>
                    </call>

                    <call id="a6" endpoint="" >
                    <parameters>
                        <label>Check quality of product</label>
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
                        <resource>Technician</resource>
                    </resources>
                    <allocation>
                    </allocation>
                    </call>
                    
                </description>
                """

                task_node = task_xml
                

                with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/drill.xml") as f: 
                    resource_et = etree.fromstring(f.read())
                
                test_allo = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
                trees = test_allo.allocate_process()
                
                for tree in trees:
                    tree = tree.intermediate_trees[0]
                    print(tree)
                    with open("xml_out.xml", "wb") as f:
                        f.write(etree.tostring(tree))

                    graphix.TreeGraph().show(etree.tostring(tree))


                    
                

