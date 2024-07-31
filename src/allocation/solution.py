from lxml import etree

from src.allocation import utils
from src.allocation.branch import Branch
import copy
import numpy as np


class Solution():
    def __init__(self, ra_pst):

        self.init_ra_pst = ra_pst  
        self.solution_ra_pst = copy.deepcopy(self.init_ra_pst) 
        self.invalid_branches = False # rename to "is_valid"
        self.is_final = False
        self.allocated_branches = []
        self.ns = {"cpee1" : list(self.init_ra_pst.nsmap.values())[0], "allo": "http://cpee.org/ns/allocation"}
        self.task_list = self.init_ra_pst.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns)
        self.tasks_iter = iter(self.task_list) # iterator 
        self.delay_deletes = [] #TODO must handle delayed deletes over multiple operations
        self.branches_to_apply = []
        self.allowed_branches = []
        self.branches = []

    def get_measure(self, measure, operator=sum, flag=False): #TODO fix calculation
        """Returns 0 if Flag is set wrong or no values are given, does not check if allocation is is_valid"""
        if flag:
            values = self.solution_ra_pst.xpath(f".//allo:allocation/cpee1:resource/cpee1:resprofile/cpee1:measures/cpee1:{measure}", namespaces=self.ns)
        else:
            values = self.solution_ra_pst.xpath(f".//cpee1:allocation/cpee1:resource/cpee1:resprofile/cpee1:measures/cpee1:{measure}", namespaces=self.ns)
        
        if self.invalid_branches:
            return np.nan
        else:
            return operator([float(value.text) for value in values])

    def check_validity(self): #TODO ensure check is done correctly
        #TODO Expand to also check if same resource is allocated in a parallel branch
        self.solution_ra_pst = etree.fromstring(etree.tostring(self.solution_ra_pst))
        tasks = self.solution_ra_pst.xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::cpee1:changepattern) and not(ancestor::cpee1:allocation)and not(ancestor::cpee1:children)]", namespaces=self.ns)

        for task in tasks:
            a = task.xpath("cpee1:allocation/*", namespaces=self.ns)
            with open("text.xml", "wb") as f:
                f.write(etree.tostring(task))
            if not task.xpath("cpee1:allocation/*", namespaces=self.ns):
                self.invalid_branches=True
                break


    def apply_branches(self, branches:list):

        for branch_no in branches:      
            task = utils.get_next_task(self.tasks_iter, self) # gets next tasks and checks for deletes
            self.branches = []
            if task == "end":
                for branch, task in self.delay_deletes:
                    if self.solution_ra_pst.xpath(f"//*[@id='{task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation) and not(ancestor::RA_RPST)]", namespaces=self.ns):
                        self.solution_ra_pst = branch.apply_to_process(self.solution_ra_pst, solution=self) # apply delays
                print(f"For solution {self} len(allocated_branches) = len(branches_to_apply): {len(self.allocated_branches) == len(self.branches_to_apply)}")
                self.is_final = True
                break

            # Try to build Branch from RA-PST
            node = self.init_ra_pst.xpath(f"//*[@id = '{task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation) and not(ancestor::RA_RPST)]", namespaces=self.ns)
            self.get_branches_for_task(node[0])

            branch = self.branches[branch_no] # get actual branch as R-RPST
            self.allocated_branches.append(branch_no)

            if branch.node.xpath("//*[@type='delete']"):
                self.delay_deletes.append((branch, task))
            else:
                self.solution_ra_pst = branch.apply_to_process(self.solution_ra_pst, solution=self) # build branch
    
    def get_possible_branches(self, force_valid=False):
        branches_list = []
        self.branches = []
        for task in self.init_ra_pst.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns):
            self.get_branches_for_task(task)
            branches_list.append(len(self.branches)-1)
            self.branches = []
        
        if not self.allowed_branches:
            self.allowed_branches = branches_list
        return branches_list
    
    def get_branches_for_task_wrap(self, node, branch=None):
        self.branches=[]
        self.get_branches_for_task(node, branch)
        return self.branches
    
    def get_branches_for_task(self, node , branch=None): # node = anchor_task
            """ 
            Delete Everything from a deepcopied node, which is not part of the new branch
            append branch to self.branches

            params:
            - node: not needed for initialization
            - branch: not needed for initialization
            """

            if node is None:
                #branch = Branch(copy.deepcopy(self.))
                self.branches.append(branch)
                node = branch.node

            if not branch:
                branch = Branch(copy.deepcopy(node))
                self.branches.append(branch)
                node=branch.node

            if node.tag == f"{{{self.ns['cpee1']}}}resprofile"or (node.tag == f"resprofile"):
                # Delete other resource profiles from branch
                parent = node.xpath("parent::node()", namespaces=self.ns)[0]

                if len(parent.xpath("*", namespaces=self.ns)) > 1:
                    to_remove = [elem for elem in parent.xpath("child::*", namespaces=self.ns) if elem != node] 
                    set(map(parent.remove, to_remove))  
                
                # Iter through children
                children = node.xpath("cpee1:children/*", namespaces=self.ns)
                branches = children, [branch for _ in children]
                
                set(map(self.get_branches_for_task, *branches))
            
            elif node.tag == f"{{{self.ns['cpee1']}}}resource" or (node.tag == f"resource"):
                # Delete other Resources from branch
                parent = node.xpath("parent::node()", namespaces=self.ns)[0]
                
                if len(parent.xpath("*", namespaces=self.ns)) > 1:
                    to_remove = [elem for elem in parent.xpath("child::*", namespaces=self.ns) if elem != node] 
                    set(map(parent.remove, to_remove))
                
                # Create a new branch for reach resource profile
                children = node.xpath("resprofile", namespaces=self.ns)
                branches = [],[]
                
                for i, child in enumerate(children):
                    path = child.getroottree().getpath(child)

                    if i > 0:    
                        new_branch = Branch(copy.deepcopy(child.xpath("/*", namespaces=self.ns)[0]))
                        self.branches.append(new_branch)
                        branches[1].append(new_branch)
                        branches[0].append(new_branch.node.xpath(path)[0])
                    else:
                        branches[0].append(child)
                        branches[1].append(branch)

                set(map(self.get_branches_for_task, *branches))
            
            elif node.tag == f"{{{self.ns['cpee1']}}}call" or node.tag == f"{{{self.ns['cpee1']}}}manipulate":
                # Create new branch for each resource
                children = node.xpath("cpee1:children/*", namespaces=self.ns)
                node_type = node.xpath("@type")

                if node_type:
                    if node_type[0] == "delete":
                        branch.open_delete = True

                if not children and node_type != 'delete':
                    # If task has no valid resource allocation, branch is_valid=False
                        branch.is_valid = False
                
                if not children and node_type == 'delete':
                    # If task must be deleted and an equivalent task is in the core process, the branch is valid
                    task_labels = [utils.get_label(etree.tostring(task)).lower() for task in self.task_list]
                    del_task = utils.get_label(etree.tostring(node).lower())
                    if del_task not in task_labels:
                        branch.is_valid = False
                            
                branches = [],[]
                for i, child in enumerate(children):

                    path = child.getroottree().getpath(child)
                    if i > 0:
                        new_branch = Branch(copy.deepcopy(child.xpath("/*", namespaces=self.ns)[0]))
                        self.branches.append(new_branch)
                        branches[1].append(new_branch)
                        branches[0].append(new_branch.node.xpath(path, namespaces=self.ns)[0])
                    else:
                        branches[0].append(child)
                        branches[1].append(branch)
                set(map(self.get_branches_for_task, *branches))
            
            else:
                raise("cpee_allocation_set_branches: Wrong node Type")

    def get_pickleable_object(self):
        
        solution = copy.deepcopy(self)
        solution.init_ra_pst = etree.tostring(solution.init_ra_pst) 
        solution.solution_ra_pst = etree.tostring(solution.solution_ra_pst) 
        solution.allocated_branches = []
        solution.ns = {"cpee1" : list(self.init_ra_pst.nsmap.values())[0], "allo": "http://cpee.org/ns/allocation"}
        solution.task_list = []
        solution.tasks_iter = None
        solution.delay_deletes = []
        solution.allowed_branches = []
        solution.branches = []

        return solution
            
            