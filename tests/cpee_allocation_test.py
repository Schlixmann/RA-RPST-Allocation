from context import src
import unittest
from lxml import etree
from xmldiff import main, formatting
from src.tree import parser, task_node as tn, gtw_node as gtw
from src.allocation import cpee_allocation
from pptree import *
from PrettyPrint import PrettyPrintTree
from src.tree import graphix
from src.allocation.solution_search import *
import time
import multiprocessing as mp
import os
import pickle


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
                graphix.TreeGraph().show(etree.tostring(branch.node), filename="branch{}".format(i), view=False)  
                with open(f"tests/branches/branch_{i}.xml", "wb") as f: 
                    f.write(etree.tostring(branch.node))
        
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

    def test_solution_creation(self):
        with open("resource_config/drill_insert_solution.xml") as f: 
                resource_et = etree.fromstring(f.read())
        with open("tests/test_xml2.xml") as f:
                task_xml = f.read()
            
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        
        trees = ProcessAllocation.allocate_process()
        print("Allocation Result: ")
        #ProcessAllocation.print_node_structure(ProcessAllocation.process.xpath("//cpee1:children", namespaces=ProcessAllocation.ns)[0])

        allocation = list(ProcessAllocation.allocations.values())[0]
        allocation.branches
        for tree in list(trees.values()):   
            
            graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0])) 
            tree.set_branches() 
                        
            with open("xml_out2.xml", "wb") as f: 
                 f.write(etree.tostring(tree.branches[0].node))

            graphix.TreeGraph().show(etree.tostring(tree.branches[0].node,), filename="branch") 
            
            
            branch = tree.branches[0].node
            with open("xml_out2.xml", "wb") as f: 
                f.write(etree.tostring(branch))
            print("New Tree: ")
            ProcessAllocation.print_node_structure(branch)
            #branch = etree.fromstring(etree.tostring(branch))
            ProcessAllocation.print_node_structure(branch)
            print(branch.xpath("/*"), " ", branch.xpath("parent::*"))

            print(branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate]"
                            "[not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns))
            test = branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns)
        

        Brute(ProcessAllocation).find_solutions()

        for i, solution in enumerate(ProcessAllocation.solutions):
            print("Solution {}: ".format(i), solution.__dict__)
            with open("tests/solutions/solution_{}.xml".format(i), "wb") as f:
                f.write(etree.tostring(solution.process))

    def test_full_solution_creation(self):
        with open("resource_config/drill_insert_solution.xml") as f: 
                resource_et = etree.fromstring(f.read())
        with open("tests/test_xml.xml") as f:
                task_xml = f.read()
            
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        
        trees = ProcessAllocation.allocate_process()
        print("Allocation Result: ")
        #ProcessAllocation.print_node_structure(ProcessAllocation.process.xpath("//cpee1:children", namespaces=ProcessAllocation.ns)[0])

        allocation = list(ProcessAllocation.allocations.values())[0]
        allocation.branches
        for tree in list(trees.values()):   
            
            graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0])) 
            tree.set_branches() 
                        
            with open("xml_out2.xml", "wb") as f: 
                 f.write(etree.tostring(tree.branches[0].node))

            #graphix.TreeGraph().show(etree.tostring(tree.branches[0].node,), filename="branch") 
            
            
            branch = tree.branches[0].node
            with open("xml_out2.xml", "wb") as f: 
                f.write(etree.tostring(branch))
            print("New Tree: ")
            #ProcessAllocation.print_node_structure(branch)
            #branch = etree.fromstring(etree.tostring(branch))
            #ProcessAllocation.print_node_structure(branch)
            print(branch.xpath("/*"), " ", branch.xpath("parent::*"))

            print(branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate]"
                            "[not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns))
            test = branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns)
        

        Brute(ProcessAllocation).find_solutions()

        for i, solution in enumerate(ProcessAllocation.solutions):
            print("Solution {}: ".format(i), solution.__dict__)
            with open("tests/solutions/solution_{}.xml".format(i), "wb") as f:
                f.write(etree.tostring(solution.process))

    def test_with_delete(self):
            with open("resource_config/drill_delete_solution.xml") as f: 
                    resource_et = etree.fromstring(f.read())
            with open("tests/test_xml.xml") as f:
                    task_xml = f.read()
                
            ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
            
            trees = ProcessAllocation.allocate_process()
            #print("Allocation Result: ")
            #ProcessAllocation.print_node_structure(ProcessAllocation.process.xpath("//cpee1:children", namespaces=ProcessAllocation.ns)[0])

            allocation = list(ProcessAllocation.allocations.values())[0]
            allocation.branches
            for i, tree in enumerate(list(trees.values())):   
                
                graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"out_{i}") 
                #tree.set_branches() 
                            
                with open("xml_out2.xml", "wb") as f: 
                    f.write(etree.tostring(tree.branches[0].node))

                #graphix.TreeGraph().show(etree.tostring(tree.branches[0].node,), filename="branch") 
                
                
                branch = tree.branches[0].node
                with open("xml_out2.xml", "wb") as f: 
                    f.write(etree.tostring(branch))
                print("New Tree: ")
                #ProcessAllocation.print_node_structure(branch)
                #branch = etree.fromstring(etree.tostring(branch))
                #ProcessAllocation.print_node_structure(branch)
                print(branch.xpath("/*"), " ", branch.xpath("parent::*"))

                print(branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate]"
                                "[not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns))
                test = branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns)
            

            Brute(ProcessAllocation).find_solutions()

            for i, solution in enumerate(ProcessAllocation.solutions):
                print("Solution {}: ".format(i), solution.__dict__)
                with open("tests/solutions/solution_{}.xml".format(i), "wb") as f:
                    f.write(etree.tostring(solution.process))

    def test_value_calc(self):
            with open("resource_config/drill_delete_solution.xml") as f: 
                    resource_et = etree.fromstring(f.read())
            with open("tests/test_xml.xml") as f:
                    task_xml = f.read()
                
            ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
            trees = ProcessAllocation.allocate_process()
            
            #for tree in list(trees.values()):
            #    tree.set_branches()

            Brute(ProcessAllocation).find_solutions()
            for sol in ProcessAllocation.solutions:
                print(sol.get_measure("cost"))
    
    def test_best(self):
        with open("resource_config/drill_delete_solution.xml") as f: 
                resource_et = etree.fromstring(f.read())
        with open("tests/test_xml.xml") as f:
                task_xml = f.read()
            
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        trees = ProcessAllocation.allocate_process()
        
        #for tree in list(trees.values()):
        #    tree.set_branches()

        
        brute_solutions = Brute(ProcessAllocation)
        brute_solutions.find_solutions()
        worst_solutions = brute_solutions.get_best_solutions("cost", max, top_n=2)
        print(worst_solutions, [list(solution.keys())[0].get_measure("cost") for solution in worst_solutions])
        best_solutions = brute_solutions.get_best_solutions("cost", min, top_n=2)
        print(best_solutions, [list(solution.keys())[0].get_measure("cost") for solution in best_solutions])

    def test_with_incomplete_resources(self):
            with open("resource_config/drill_delete_solution_incomplete.xml") as f: 
                    resource_et = etree.fromstring(f.read())
            with open("tests/test_processes/test_insuf_resources_delete.xml") as f:
                    task_xml = f.read()
                
            ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
            
            trees = ProcessAllocation.allocate_process()
            #print("Allocation Result: ")
            #ProcessAllocation.print_node_structure(ProcessAllocation.process.xpath("//cpee1:children", namespaces=ProcessAllocation.ns)[0])

            allocation = list(ProcessAllocation.allocations.values())[0]
            allocation.branches
            for i, tree in enumerate(list(trees.values())):   
                
                graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"out_{i}") 
                #tree.set_branches() 
                            
                with open("xml_out2.xml", "wb") as f: 
                    f.write(etree.tostring(tree.branches[0].node))

                #graphix.TreeGraph().show(etree.tostring(tree.branches[0].node,), filename="branch") 
                
                
                branch = tree.branches[0].node
                with open("xml_out2.xml", "wb") as f: 
                    f.write(etree.tostring(branch))
                print("New Tree: ")
                #ProcessAllocation.print_node_structure(branch)
                #branch = etree.fromstring(etree.tostring(branch))
                #ProcessAllocation.print_node_structure(branch)
                print(branch.xpath("/*"), " ", branch.xpath("parent::*"))

                print(branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate]"
                                "[not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns))
                test = branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns)
            

            Brute(ProcessAllocation).find_solutions()

            for i, solution in enumerate(ProcessAllocation.solutions):
                #solution.check_validity()
                print("Solution {}: ".format(i), solution.__dict__)
                with open("tests/solutions/solution_{}.xml".format(i), "wb") as f:
                    f.write(etree.tostring(solution.process))
            
    def test_new_find_solutions(self):
            with open("resource_config/drill_delete_solution_incomplete.xml") as f: 
                    resource_et = etree.fromstring(f.read())
            with open("tests/test_processes/test_insuf_resources_delete.xml") as f:
                    task_xml = f.read()
                
            ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
            
            trees = ProcessAllocation.allocate_process()
            #print("Allocation Result: ")
            #ProcessAllocation.print_node_structure(ProcessAllocation.process.xpath("//cpee1:children", namespaces=ProcessAllocation.ns)[0])

            allocation = list(ProcessAllocation.allocations.values())[0]
            allocation.branches
            for i, tree in enumerate(list(trees.values())):   
                
                #graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"out_{i}") 
                #tree.set_branches() 
                            
                with open("xml_out2.xml", "wb") as f: 
                    f.write(etree.tostring(tree.branches[0].node))

                #graphix.TreeGraph().show(etree.tostring(tree.branches[0].node,), filename="branch") 
                
                
                branch = tree.branches[0].node
                with open("xml_out2.xml", "wb") as f: 
                    f.write(etree.tostring(branch))
                print("New Tree: ")
                #ProcessAllocation.print_node_structure(branch)
                #branch = etree.fromstring(etree.tostring(branch))
                #ProcessAllocation.print_node_structure(branch)
                print(branch.xpath("/*"), " ", branch.xpath("parent::*"))

                print(branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate]"
                                "[not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns))
                test = branch.xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ProcessAllocation.ns)
            

            brute_solutions = Brute(ProcessAllocation)
            brute_solutions.find_solutions()

            for i, solution in enumerate(brute_solutions.solutions):
                #solution.check_validity()
                print("Solution {}: ".format(i), solution.__dict__)
                with open("tests/solutions/solution_{}.xml".format(i), "wb") as f:
                    f.write(etree.tostring(solution.process))
    
    def test_short_process(self):
            with open("resource_config/offer_resources.xml") as f: 
                    resource_et = etree.fromstring(f.read())
            with open("tests/test_processes/offer_process_short.xml") as f:
                    task_xml = f.read()
            show_graph = False
                
            ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
            trees = ProcessAllocation.allocate_process()

            allocation = list(ProcessAllocation.allocations.values())[0]
            allocation.branches
            for i, tree in enumerate(list(trees.values())):   
                
                if show_graph:
                    graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"out_{i}") 

            start = time.time()
            brute_solutions = Brute(ProcessAllocation)
            brute_solutions.find_solutions()
            end = time.time()

            print("Number of Solutions: {}".format(len(brute_solutions.solutions)))
            print("Solutions found in: {} s".format(end-start))

            measure = "cost"
            ProcessAllocation.solutions = brute_solutions.solutions
            best_solutions = brute_solutions.get_best_solutions(measure, include_invalid=False, top_n=5)
            print(best_solutions)

            #for i, solution in enumerate(best_solutions):
            #    with open(f"tests/benchmarks/best_brute_{i}.xml", "wb") as f:
            #        key = next(iter(solution))
            #        f.write(etree.tostring(key.process))             
            
            for i, solution in enumerate(best_solutions):
                with open(f"tests/solutions/test_short_proc_{i}.xml", "wb") as f:
                    f.write(etree.tostring(list(solution.keys())[0].process))

                with open(f"tests/benchmarks/test_short_proc_{i}.xml", "rb") as f:
                    key = next(iter(solution))            
                    test_solution = Solution(etree.fromstring(f.read()))
                    self.assertEqual(key.get_measure(measure), test_solution.get_measure(measure))

    def test_long_process(self):
            with open("resource_config/offer_resources.xml") as f: 
                    resource_et = etree.fromstring(f.read())
            with open("tests/test_processes/offer_process.xml") as f:
                    task_xml = f.read()
            show_graph = False
                
            ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
            trees = ProcessAllocation.allocate_process()

            allocation = list(ProcessAllocation.allocations.values())[0]
            allocation.branches
            for i, tree in enumerate(list(trees.values())):   
                
                if show_graph:
                    graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"out_{i}") 

            start = time.time()
            brute_solutions = Brute(ProcessAllocation)
            brute_solutions.find_solutions()
            end = time.time()

            print("Number of Solutions: {}".format(len(brute_solutions.solutions)))
            print("Solutions found in: {} s".format(end-start))

            measure = "cost"
            ProcessAllocation.solutions = brute_solutions.solutions
            best_solutions = brute_solutions.get_best_solutions(measure, include_invalid=False, top_n=5)
            print(best_solutions)

            #for i, solution in enumerate(best_solutions):
            #    with open(f"tests/benchmarks/best_brute_{i}.xml", "wb") as f:
            #        key = next(iter(solution))
            #        f.write(etree.tostring(key.process))             
            
            for i, solution in enumerate(best_solutions):
                with open(f"tests/solutions/test_long_proc_brute_{i}.xml", "wb") as f:
                    f.write(etree.tostring(list(solution.keys())[0].process))

                with open(f"tests/benchmarks/test_short_proc_{i}.xml", "rb") as f:
                    key = next(iter(solution))            
                    test_solution = Solution(etree.fromstring(f.read()))
                    self.assertEqual(key.get_measure(measure), test_solution.get_measure(measure))
                

    def test_all_options_brute(self):
            with open("resource_config/all_options.xml") as f: 
                    resource_et = etree.fromstring(f.read())
            with open("tests/test_processes/test_insuf_resources_delete.xml") as f:
                    task_xml = f.read()
            
            show_graphs = False
            ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
            trees = ProcessAllocation.allocate_process()
            allocation = list(ProcessAllocation.allocations.values())[0]

            for i, tree in enumerate(ProcessAllocation.allocations.values()):   
                
                if show_graphs:  
                    graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"out_{i}")
                    
                if i == 1:
                    for i, branch in enumerate(tree.branches):
                        if show_graphs:
                            graphix.TreeGraph().show(etree.tostring(branch.node), filename=f"branch_{i}")

            brute_solutions = Brute(ProcessAllocation)
            brute_solutions.find_solutions()

            for i, solution in enumerate(brute_solutions.solutions):
                with open(f"tests/benchmarks/test_all_options_{i}.xml", "rb") as f:
                    self.assertEqual(etree.tostring(solution.process), f.read())

    def test_long_process_pickle(self):
        with open("resource_config/offer_resources_heterogen.xml") as f: 
                resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_paper.xml") as f:
                task_xml = f.read()
        show_graph = False
            
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        trees = ProcessAllocation.allocate_process()

        allocation = list(ProcessAllocation.allocations.values())[0]
        allocation.branches
        for i, tree in enumerate(list(trees.values())):   
            
            if show_graph:
                graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"out_{i}") 

        start = time.time()
        brute_solutions = Brute(ProcessAllocation)
        opts, tasklist = brute_solutions.get_all_opts()
        #brute_solutions.find_solutions_pickle(opts)       
        opts = [list(o.values())[0] for o in opts]
        b = brute_solutions.iter_product(opts)
        solutions = opts
        measure = "cost"
        results = brute_solutions.find_solutions(b, "cost")
        end = time.time()
        


        best_solutions = combine_pickles()
        
        for b in best_solutions:
            print(b)
        print(f"Execution time was: {end-start}")
        print(f"Execution time in min was: {(end-start)/60}")

        with open("tmp/results/best/best_solution.pkl", "wb") as f:
            pickle.dump(best_solutions, f)

    def test_short_process_pickle(self):
        with open("resource_config/offer_resources_cascade_del.xml") as f: 
                resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_short.xml") as f:
                task_xml = f.read()
        show_graph = False
            
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        trees = ProcessAllocation.allocate_process()

        allocation = list(ProcessAllocation.allocations.values())[0]
        allocation.branches
        for i, tree in enumerate(list(trees.values())):   
            
            if show_graph:
                graphix.TreeGraph().show(etree.tostring(tree.intermediate_trees[0]), filename=f"out_{i}") 

        start = time.time()
        brute_solutions = Brute(ProcessAllocation)
        opts, tasklist = brute_solutions.get_all_opts()
        #brute_solutions.find_solutions_pickle(opts)       
        opts = [list(o.values())[0] for o in opts]
        b = brute_solutions.iter_product(opts)
        solutions = opts
        measure = "cost"
        results = brute_solutions.find_solutions(b, "cost")
        print(results)
        end = time.time()

        best_solutions = combine_pickles()

        for b in best_solutions:
            print(b)
        
        with(open("tests/solutions/best_brute_1.xml", "rb")) as f:
            target_process = f.read()
        self.assertEqual(target_process, best_solutions[-1]["solution"].process, "The target process should be the same as the resulting one")

        
        
        print(f"Execution time was: {(end-start):.2f}")
        print(f"Execution time in min was: {(end-start)/60:.2f}")
    
    def test_retrieve_pickle(self):
        with open("resource_config/offer_resources_close_maxima.xml") as f: 
                resource_et = etree.fromstring(f.read())
        with open("tests/test_processes/offer_process_paper.xml") as f:
                task_xml = f.read()
        show_graph = False
            
        ProcessAllocation = cpee_allocation.ProcessAllocation(task_xml, resource_url=resource_et)
        trees = ProcessAllocation.allocate_process()
        brute_solutions = Brute(ProcessAllocation)
        #opts = brute_solutions.get_all_opts()
        a = brute_solutions.retrieve_pickle("tmp/test_pkl_3.pkl")

        print(a[:10])

    def test_build_best(self):
        with open("tmp/results/best_solution", "rb") as f:
            best = pickle.load(f)
            process = best[-1]["solution"].process
        
        with open("xml_out.xml", "wb") as f:
            f.write(process)
        
        best1 = best[-1]
        best1["solution"].process = etree.fromstring(best1["solution"].process)
        print(best1["solution"].get_measure("cost", flag=True))

    def test_combine_pickles(self):
        combine_pickles()

    def test_insert_from_pickle(self):
        with open("tests/test_processes/offer_process_paper.xml") as f: 
            task_xml = f.read()
        with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/offer_resources_heterogen.xml") as f:
            resource_et = etree.fromstring(f.read())
        
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
        trees = process_allocation.allocate_process()

        test = (0,1,0,2,0,1,0,0,0,3)

        measure = "cost"
        start = time.time()
        brute_solutions = Brute(process_allocation)
        solutions, tasklist = brute_solutions.get_all_opts()
        single_solution = {}
        for i, d in enumerate(solutions):
            print(d.items())
            k,v = list(d.items())[0]
            single_solution[k] = [test[i]]
        solutions = [{k: [v[0], 0]} for k, v in single_solution.items()]
        solutions = [list(o.values())[0] for o in solutions]
        b = brute_solutions.iter_product(solutions)
        results = brute_solutions.find_solutions(b, measure)
        outcome = combine_pickles()
        end = time.time()
        print(outcome)

    
    def test_build_ra_rpst(self):
        with open("tests/test_processes/offer_process_paper.xml") as f: 
            task_xml = f.read()
        with open("/home/felixs/Programming_Projects/RDPM_private/resource_config/offer_resources_heterogen.xml") as f:
            resource_et = etree.fromstring(f.read())
        
        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
        trees = process_allocation.allocate_process()

        ra_rpst = process_allocation.get_ra_rpst()
                
        with open("ra_rpst.xml", "wb") as f:
            f.write(ra_rpst)
            
            
    def test_heur_opts(self):
        process = "processes/offer_process_paper.xml"
        resources = "resource_config/offer_resources_many_invalid_branches.xml"
        with open(process) as f:
            task_xml = f.read()
        
        with open(resources) as f:
            resource_et = etree.fromstring(f.read())

        heuristic_config = {"top_n":2, "include_invalid":False, "measure":"cost"}

        process_allocation = ProcessAllocation(task_xml, resource_url=resource_et)
        trees = process_allocation.allocate_process()
        start = time.time()
        brute_solutions = Brute(process_allocation)
        brute_solutions.find_solutions_with_heuristic(top_n=2, force_valid=True)
        ProcessAllocation.solutions = brute_solutions.solutions
        outcome = brute_solutions.get_best_solutions(heuristic_config["measure"], 
                                                    include_invalid=heuristic_config["include_invalid"], top_n=10)
        end = time.time()
        
        with open("test_heur_paper.xml", "wb") as f:
            f.write(etree.tostring(outcome[-1]["solution"].process))

        print(outcome)
        print(f"Time: {end-start}")
        
        print("Invalid Branches? ", [ind["solution"].invalid_branches for ind in outcome])