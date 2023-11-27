import uuid
import json
import warnings
import logging
import os
logger = logging.getLogger(__name__)

class Node:
    # Class Variables:
    ns = {}

    def __init__(self, config_file="etree_config.json"):
        self.__id = str(uuid.uuid1())
        self.children = []
        self.expected_time = 0
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        config_abs = os.path.join(parent_dir, self.config_file)
        with open(config_abs, 'r') as f:
            config = json.load(f)
            Node.ns = config["namespaces"]["cpee"]

    def add_child(self, obj):
        self.children.append(obj)

    @property
    def id(self):
        return self.__id

    def tree_paths(self, stack = [], i=0):
        if len(self.children) == 0:
                return [self]
        if self.node_type == "task":   
            # TODO decide on best resource based on measurement 
            # current decision: first in line [0]
            return [self] + [path for child in self.children for path in child.tree_paths()]
        else: 
            return [self] + [child.tree_paths() for child in self.children]
    
    def count_branch_steps(self, measure=None, operator=min):

        if self.node_type == "task":
            return operator([child.count_branch_steps(measure=measure, operator=min) for child in self.children])
        
        elif self.node_type == "resource" and len(self.children) == 0:
            return self.measure[measure]
        
        return self.measure[measure] +  sum([child.count_branch_steps(measure, operator) for child in self.children])


    def clean_best_branch_node(self, measure, operator):

        if len(self.children) == 0:
            return self 
        if self.node_type != "resource":
            self.children = [self.get_best_child_node(measure, operator)]
    
        for child in self.children:
            child.clean_best_branch_node(measure, operator)

    #TODO Def best res_node
    # Decide between multiple resource children and return the best one based on the value of all its children.
    #
    def get_best_child_node(self, measure=None, operator=None):
        branch_measure = [child.count_branch_steps(measure=measure, operator=operator) for child in self.children]
        if not operator:
            value = min(branch_measure)
        else:
            value = operator(branch_measure)
        index = branch_measure.index(value)
        return self.children[index]

    def get_best_branch(self, measure=None, operator=None):
        # TODO should return all indices not just first. 
        #       
        print(f"To get the best branch, the used operator is: {operator} on the measure {measure}")
        all_branches = [child.tree_paths() for child in self.children]
        print(all_branches)
        branch_measure = [branch.count_branch_steps(measure=measure, operator=operator) for branch in self.children]#[len(branch) for branch in all_branches]
        print(f"Branch measure, measure = {measure}: {branch_measure}")
        if not operator:
            value = min(branch_measure)
        else:
            value = operator(branch_measure)
        index = branch_measure.index(value)

        best_branch =  all_branches[index]       
        
        # clean node:
        best_res_node = best_branch[0]
        best_res_node.clean_best_branch_node(measure, operator)
        best_node = self
        best_node.children = [best_res_node]
        best_branch = [self] + best_branch
        return best_branch, branch_measure, value, best_node

    def filter_nested_list(self, nested_list, node_type="resource"):
        open_list = [element for element in nested_list if type(element) == list]
        finished_list = [element for element in nested_list if (type(element) != list) and (getattr(element, "node_type") == node_type)]
        open_list = [step for sublist in open_list for step in sublist]
        if len(open_list) == 0:
            return finished_list
        return finished_list + self.filter_nested_list(open_list, node_type=node_type)
    
    def get_all_nodes(self, key="resource"):
        # if len(self.children) == 0:
        #     return [self]
        # for child in self.children:
        #     if self.node_type == key:
        #         return [self] + child.get_all_resource_nodes()
        #     else:
        #         return child.get_all_resource_nodes()
        nodes = self.tree_paths()
        nodes = self.filter_nested_list(nodes, node_type=key)
        return nodes
    
    def get_change_operations(self):
        operations = [node.resource_profile.change_patterns for node in self.filter_nested_list(self.tree_paths(), node_type="resource")]
        change_operations = []
        for operation in operations:
            if len(operation) > 0:
                for pattern in operation:
                    change_operations.append({"resource": pattern, "type": pattern.attrib["type"]})
            else:
                change_operations.append({"resource": pattern, "type": "allocation"})
        return change_operations
    

    # TODO 
    # create method "get_best_branch" based on different optimization types (e.g. min/max/avg)
    #  -> different values from Resource Profile (sum of rp expected values)
    