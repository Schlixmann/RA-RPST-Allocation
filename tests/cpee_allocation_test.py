from context import tree_allocation
import unittest
from lxml import etree
from xmldiff import main, formatting
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
        with open("tests/test_xml.xml") as f:
            task_xml = f.read()

        task_node = task_xml
        

        with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/drill.xml") as f: 
            resource_et = etree.fromstring(f.read())
        
        test_allo = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        trees = test_allo.allocate_process()
        
        for tree in list(trees.values()):
            graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0])) 
            
            with open("xml_out2.xml", "wb") as f:
                    f.write(etree.tostring(tree.intermediate_trees[0]))
            #print("tree branches:", tree.branches())


            tree.set_branches()
            print("tree.branches: ", tree.branches)
            i = 0
            for branch in tree.branches:
                i += 1
                graphix.TreeGraph().show(etree.tostring(branch), filename="branch{}".format(i), view=False)  
                with open(f"tests/branches/branch_{i}.xml", "wb") as f: 
                    f.write(etree.tostring(branch))
        
        with open("tests/branches/branch_4.xml") as a, open("tests/branches/branch_2.xml") as b:
            diff = main.diff_files(a,b)#, formatter=formatting.XMLFormatter())
            #self.assertEqual(diff, [], f"The difference between the XML's is {diff}")

    def test_process_allo_Branches(self):
            with open("tests/test_xml.xml") as f:
                task_xml = f.read()

            task_node = task_xml
            

            with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/drill.xml") as f: 
                resource_et = etree.fromstring(f.read())
            
            test_allo = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
            trees = test_allo.allocate_process()
            
            for tree in list(trees.values()):
                
                graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0])) 
                
                with open("xml_out2.xml", "wb") as f:
                        f.write(etree.tostring(tree.intermediate_trees[0]))
                #print("tree branches:", tree.branches())


                tree.set_branches()
                print("tree.branches: ", tree.branches)
                i = 0
                for branch in tree.branches:
                    print("Branch Attrib:", branch.open_delete)
                    branch = branch.node
                    i += 1
                    graphix.TreeGraph().show(etree.tostring(branch), filename="branch{}".format(i), view=True)  
                    with open(f"tests/branches/branch_{i}.xml", "wb") as f: 
                        f.write(etree.tostring(branch))
            
            with open("tests/branches/branch_4.xml") as a, open("tests/branches/branch_2.xml") as b:
                diff = main.diff_files(a,b)#, formatter=formatting.XMLFormatter())
                #self.assertEqual(diff, [], f"The difference between the XML's is {diff}")

    def test_full_process_allo(self):
                with open("main_process.xml") as f:
                      task_xml = f.read()

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

    def test_solution_creation(self):
        with open("resource_config/drill_insert_solution.xml") as f: 
                resource_et = etree.fromstring(f.read())
        with open("tests/test_xml2.xml") as f:
                task_xml = f.read()
            
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        trees = ProcessAllocation.allocate_process()

        for tree in list(trees.values()):   
              
            graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0])) 
            tree.set_branches() 
        
        task1_branch1 = list(ProcessAllocation.allocations.values())[0].branches[2]
        process = ProcessAllocation.apply_branch_to_process(task1_branch1.node)
        with open("xml_out.xml", "wb") as f:
            f.write(etree.tostring(process))

    def test_full_solution_creation(self):
        with open("resource_config/drill_insert_solution.xml") as f: 
                resource_et = etree.fromstring(f.read())
        with open("tests/test_xml2.xml") as f:
                task_xml = f.read()
            
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        
        trees = ProcessAllocation.allocate_process()
        print("Allocation Result: ")
        ProcessAllocation.print_node_structure(ProcessAllocation.process.xpath("//cpee1:children", namespaces=ProcessAllocation.ns)[0])

        for tree in list(trees.values()):   
              
            graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0])) 
            tree.set_branches() 
        

        ProcessAllocation.find_solutions()

        for i, solution in enumerate(ProcessAllocation.solutions):
            print("Solution {}: ".format(i), solution.__dict__)
            with open("tests/solutions/solution_{}.xml".format(i), "wb") as f:
                f.write(etree.tostring(solution.process))


