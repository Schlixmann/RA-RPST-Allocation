# Import modules
from tree_allocation.allocation.branch import Branch
from tree_allocation.tree import task_node as tn
from tree_allocation.tree import res_node as rn, R_RPST
from tree_allocation.helpers import get_all_resources, get_all_tasks, get_process_model
from tree_allocation.proc_resource import *
from tree_allocation.tree import graphix

# Import external packages
from PrettyPrint import PrettyPrintTree
from lxml import etree
import uuid
import warnings
import logging
import copy
import threading
logger = logging.getLogger(__name__)

class ProcessAllocation(): 
    """
    Call TaskAllocation() for every task in the process (extra: --> Define area which should be allocated)
    - should be super of TaskAllocation
    The call must be done in a threaded and Async fashion, thus: 
    - Every Task allocation must run as a thread which has a state out of the task allocation steps. 
    - eventually when all allocations have either reached "stopped" or "finished" all issues of stopped branches must be resolved. 
    - the costs of the changes must be calculated and used in the allocation decision.

    - Allocation idea: Build all possible valid processes and search for best one
    """

    def __init__(self, process:str, resource_url) -> None:
        self.id = str(uuid.uuid1())
        self.process = etree.fromstring(process)
        self.resource_url = resource_url
        self.valid_allocations = []
        self.allocations = {}
        self.solutions = []
        self.ns = None
        self.ra_rpst:str = None
     
    def allocate_process(self):
        """ 
        This method triggers the threaded allocation of each task in the process
        - if in parallel or XOR maybe add a flag?!
        """
        # TODO Tasks must still be adapted, only for testing purposes now
        self.ns = {"cpee1" : list(self.process.nsmap.values())[0]}
        tasks = self.process.xpath("//cpee1:call|//cpee1:manipulate", namespaces=self.ns)
        allocations = []
        threads = []

        event = threading.Event() # Event set to true, if all deletes have been cleared
        for task in tasks: 
            print("The task is: ", task)
            allocation = TaskAllocation(self, etree.tostring(task))
            x = threading.Thread(target=self.add_allocation, args=(task, allocation.allocate_task(None, self.resource_url),))
            self.allocations[task.xpath("@id")[0]] = (allocation)
            threads.append(x)
            x.start()

        for thread in threads:
            thread.join()
        
        for allocation in list(self.allocations.values()):
            allocation.set_branches()

        #TODO: can be deleted
        # delete in own tree:
        for allocation in allocations:
            if allocation.open_delete:
                delete_tasks = allocation.intermediate_trees[-1].xpath("//cpee1:manipulate[@type='delete']|//cpee1:call[@type='delete']", namespaces=self.ns)
                
                for delete_task in delete_tasks:
                    label = R_RPST.get_label(etree.tostring(delete_task))
                    hits = allocation.intermediate_trees[0].xpath(f"//cpee1:*[@label='{label}']|//cpee1:parameters[cpee1:label='{label}']", namespaces=self.ns)
                    [hit for hit in hits if not hit.xpath("@type='delete'")]
                    #TODO -> should only be allowed to delete in branches which are not the delete branch is part of
                    # Implement
        
        return self.allocations
    
    def add_allocation(self, task, output):
        #task.xpath("cpee1:allocation", namespaces=self.ns)[0].append(output)
        pass

    def get_ra_rpst(self) -> str:
        if not self.ra_rpst:
            self.build_ra_rpst()
        return self.ra_rpst

    def build_ra_rpst(self) -> None:
        """
        Build the RA-RPST from self.allocations
        - The Allocation trees are part of the Cpee-Tree und the tag ra_rpst
        - if self.allocations = {} -> call self.allocate_process()

        return: 
            RA-RPST as xml String in CPEE-Tree format.
        """
        if not self.allocations:
            self.allocate_process()

        process = copy.deepcopy(self.process)

        for key, value in self.allocations.items():
            node = process.xpath(f"//*[@id='{str(key)}']", namespaces = self.ns)[0]
            node.append(etree.Element("ra_rpst")) # add new node ra_rpst
            node.xpath("ra_rpst")[0].append(value.intermediate_trees[0].xpath("cpee1:children", namespaces=self.ns)[0]) # add allocation tree
        
        self.ra_rpst = etree.tostring(process)

    def get_best_solution(self, measure, operator=min, consider_all_solutions=True):
        solutions_to_evaluate = self.solutions if not consider_all_solutions else filter(lambda x: x.invalid_branches == False, self.solutions)
        solution_measure = {solution: solution.get_measure(measure) for solution in solutions_to_evaluate}
        return operator(solution_measure, key=solution_measure.get)
    
    def print_node_structure(self, node=None, level=0):
        if node is None:
            node = self.process
        print('  ' * level + node.tag)
        for child in node.xpath("*"):
            self.print_node_structure(child, level + 1)

class TaskAllocation(ProcessAllocation):

    def __init__(self, parent:ProcessAllocation, task:str, state='initialized' ) -> None:
        allowed_states = {'ready', 'running', 'stopped', 'finished', 'initialized'}

        self.parent = parent
        self.process = self.parent.process
        self.task = task
        self.state = state
        self.final_tree = None
        self.intermediate_trees = [] # etree
        self.invalid_branches:bool = False
        self.branches:list = []
        
        self.lock:bool = False
        self.open_delete = False
        self.ns = None
    
    def set_branches(self, node=None, branch_obj=None):
        """ 
        Delete Everything from a deepcopied node, which is not part of the new branch
        append branch to branches

        To do removal: 
        build deep_copy to keep original node!
        go through all Resprofiles
        create new branch for each resprofile( -> from root)
        Delete all other resprofiles except current one. Element.remove! 
        deepcopy = self.task (otherwise tasknode is changed!)  
        """

        if node is None:
            branch_obj = Branch(copy.deepcopy(self.intermediate_trees[0]))
            self.branches.append(branch_obj)
            node = branch_obj.node
        

        if node.tag == f"{{{self.ns['cpee1']}}}resprofile"or (node.tag == f"resprofile"):
            # Delete other resource profiles from branch
            parent = node.xpath("parent::node()", namespaces=self.ns)[0]

            if len(parent.xpath("*", namespaces=self.ns)) > 1:
                to_remove = [elem for elem in parent.xpath("child::*", namespaces=self.ns) if elem != node] 
                set(map(parent.remove, to_remove))  
            
            # Iter through children
            children = node.xpath("cpee1:children/*", namespaces=self.ns)
            branches = children, [branch_obj for _ in children]
            
            set(map(self.set_branches, *branches))
        
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
                    branches[1].append(branch_obj)

            set(map(self.set_branches, *branches))
        
        elif node.tag == f"{{{self.ns['cpee1']}}}call" or node.tag == f"{{{self.ns['cpee1']}}}manipulate":
            # Create new branch for each resource
            children = node.xpath("cpee1:children/*", namespaces=self.ns)
            node_type = node.xpath("@type")

            if node_type:
                node_type = node_type[0]
                if node_type == "delete":
                    branch_obj.open_delete = True

            if not children and node_type != 'delete':
                branch_obj.valid = False
                        
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
                    branches[1].append(branch_obj)
            set(map(self.set_branches, *branches))
        
        else:
            raise("cpee_allocation_set_branches: Wrong node Type")

    def allocate_task(self, root=None, resource_url=None, excluded=[]):
        """
        Build the allocation tree for self.task. 
        -> set self.state = running
        -> Resources = Request from Resource Repository
        -> Build allo_tree(task, resources)
        -> if hitting delete or only invalid branches: 
            -> set self.allo_tree = allo_tree
            -> set self.state = stopped
        -> if valid branch: 
            -> set self.state = finished
        -> Choose best branch (Local best allocation)

        -> If Global best allocation becomes interesting: provide ordered list
        """

        if root is None:
            self.state='running'
            root = etree.fromstring(self.task)
            print("New created root: ", root)
            self.ns = {"cpee1" : list(root.nsmap.values())[0]}
            root.append(etree.Element(f"{{{self.ns['cpee1']}}}children"))
            self.intermediate_trees.append(copy.deepcopy(self.allocate_task(root, resource_url=resource_url, excluded=[root])))
            return self.intermediate_trees[0]
        else:
            root.append(etree.Element(f"{{{self.ns['cpee1']}}}children"))
            if root.attrib["id"] == "a9":
                print("a")
            print("Task to allocate: ", R_RPST.get_label(etree.tostring(root)))

        res_xml = copy.deepcopy(resource_url)
        # Create Resource Children
        for resource in res_xml.xpath("*"):

            #Delete non fitting profiles
            for profile in resource.xpath("resprofile"):
                profile.append(etree.Element(f"{{{self.ns['cpee1']}}}children"))
                
                if not (R_RPST.get_label(etree.tostring(root).lower()) == profile.attrib["task"].lower() and (profile.attrib["role"] in R_RPST.get_allowed_roles(etree.tostring(root)) if len(R_RPST.get_allowed_roles(etree.tostring(root))) > 0 else True)):
                    resource.remove(profile)
            
            # Add Resource if it has fitting profiles
            if len(resource.xpath("*")) > 0:
                root.xpath("cpee1:children", namespaces=self.ns)[0].append(resource)
                
        task_elements = R_RPST.CpeeElements().task_elements
        #print("Root before Tasks: ")
        #self.print_node_structure(root)

        # End condition for recursive call
        if len(root.xpath("cpee1:children", namespaces = self.ns)) == 0: # no task parents exist
            if len([parent for parent in root.xpath("ancestor::cpee1:*", namespaces=self.ns) if parent.tag in task_elements]) == 0: 
                warnings.warn("No resource for a core task")
                raise(ResourceError(root))
            else:
                task_parents = [parent for parent in root.xpath("ancestor::cpee1:*", namespaces=self.ns) if parent.tag in task_elements]
                task_parent = task_parents[-1]

            if len(task_parent.xpath("cpee1:children/*", namespaces=self.ns)) == 0:
                warnings.warn("The task can not be allocated due to missing resource availability", ResourceWarning)
                raise(ResourceError(task_parent))
            
            return root
        #excluded_ini = copy.copy(excluded)
        # Add next tasks to the tree
        for profile in root.xpath("cpee1:children/resource/resprofile", namespaces=self.ns):
            ex_branch = copy.copy(excluded)

            for change_pattern in profile.xpath("changepattern"):
                cp_tasks = [element for element in change_pattern.xpath(".//*") if element.tag in task_elements]
                cp_task_labels = [R_RPST.get_label(etree.tostring(task)).lower() for task in cp_tasks]
                ex_tasks =  [R_RPST.get_label(etree.tostring(task)).lower() for task in ex_branch]
                
                #TODO excluded tasks
                if any(x in ex_tasks or x == R_RPST.get_label(etree.tostring(root)) for x in cp_task_labels): 
                    print(f"Break reached, task {[x for x in cp_task_labels if x in ex_tasks]} in excluded")
                    root.xpath("cpee1:children/resource/resprofile", namespaces=self.ns).remove(profile)
                    continue

                for task in cp_tasks:

                    attribs = {"type": change_pattern.xpath("@type"), "direction": change_pattern.xpath("parameters/direction/text()")}
                    task.attrib.update({key: value[0].lower() for key, value in attribs.items() if value}) 
                    
                    if change_pattern.xpath("@type")[0].lower() in ["insert", "replace"]:                           
                        path = etree.ElementTree(task.xpath("/*")[0]).getpath(task) # generate path to current task
                        task = copy.deepcopy(task.xpath("/*")[0]).xpath(path)[0]    # Deepcopy whole tree and re-locate current task
                        ex_branch.append(task)
                        if change_pattern.xpath("@type")[0].lower() in ["replace"]:   
                            print("stop")
                        profile.xpath("cpee1:children", namespaces=self.ns)[0].append(self.allocate_task(task, resource_url, excluded=ex_branch))
                        
                    elif change_pattern.xpath("@type")[0].lower() == "delete":
                        self.lock = True
                        profile.xpath("cpee1:children", namespaces=self.ns)[0].append(task)
                        self.open_delete = True
                        # Branch ends here

                    else:
                        raise("Changepattern type not in ['insert', 'replace', 'delete']")
    
        return root
    
    def print_node_structure(self, node, level=0):
        print('  ' * level + node.tag + ' ' + str(node.attrib))
        for child in node.xpath("*"):
            self.print_node_structure(child, level + 1)

class ResourceError(Exception):
    # Exception is raised if no sufficiant allocation for a task can be found for available resources
    
    def __init__(self, task, message="{} No valid resource allocation can be found for the given set of available resources"):
        self.task = task
        self.message = message.format(R_RPST.get_label(etree.tostring(self.task)))
        super().__init__(self.message)

class ResourceWarning(UserWarning):
    pass