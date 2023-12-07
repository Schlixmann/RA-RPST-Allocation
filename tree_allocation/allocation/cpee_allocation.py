# Import modules
from tree_allocation.tree import task_node as tn
from tree_allocation.tree import res_node as rn, R_RPST
from tree_allocation.helpers import get_all_resources, get_all_tasks, get_process_model
from tree_allocation.allocation.change_operations import *
from tree_allocation.proc_resource import *

# Import external packages
from PrettyPrint import PrettyPrintTree
from lxml import etree
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
        self.ns = None
     
    def allocate_process(self):
        """ 
        This method triggers the threaded allocation of each task in the process
        - if in parallel or XOR maybe add a flag?!
        """
        # TODO Tasks must still be adapted, only for testing purposes now
        self.ns = {"cpee1" : list(self.process.nsmap.values())[0]}
        tasks = self.process.xpath("cpee1:call", namespaces=self.ns)
        allocations = []
        threads = []
        print(self.resource_url)
        print(tasks)

        event = threading.Event() # Event set to true, if all deletes have been cleared
        for task in tasks: 
            print("The task is: ", task)
            allocation = TaskAllocation(self, etree.tostring(task))
            x = threading.Thread(target=allocation.allocate_task, args=(None, self.resource_url))
            allocations.append(allocation)
            threads.append(x)
            x.start()
        
        for thread in threads:
            thread.join()


        # delete in own tree:
        for allocation in allocations:
            if allocation.open_delete:
                delete_tasks = allocation.intermediate_trees[-1].xpath("//cpee1:manipulate[@type='delete']|//cpee1:call[@type='delete']", namespaces=self.ns)
                
                for delete_task in delete_tasks:
                    label = R_RPST.get_label(etree.tostring(delete_task))
                    hits = allocation.intermediate_trees[0].xpath(f"//cpee1:*[@label='{label}']|//cpee1:parameters[cpee1:label='{label}']", namespaces=self.ns)
                    [hit for hit in hits if not hit.xpath("@type='delete")]
                    #TODO -> should only be allowed to delete in branches which are not the delete branch is part of
                    # Implement

        return allocations
        

class TaskAllocation(ProcessAllocation):

    def __init__(self, parent:ProcessAllocation, task:str, state='initialized' ) -> None:
        allowed_states = {'ready', 'running', 'stopped', 'finished', 'initialized'}


        self.parent = parent
        self.process = self.parent.process
        self.task = task
        self.state = state
        self.final_tree = None
        self.intermediate_trees = []
        
        self.lock:bool = False
        self.open_delete = False
        self.ns = None

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
            return self.intermediate_trees.append(self.allocate_task(root, resource_url=resource_url))
        else:
            root.append(etree.Element(f"{{{self.ns['cpee1']}}}children"))
            print("Task to allocate: ", R_RPST.get_label(etree.tostring(root)))

        res_xml = copy.deepcopy(resource_url)
        av_resources = res_xml.xpath("resource") # available resources
        x = res_xml.xpath("*")
        # Create Resource Children
        for resource in av_resources:
            
            #Delete non fitting profiles
            for profile in resource.xpath("resprofile"):
                profile.append(etree.Element("children"))
                #print("Profile description: ", profile.xpath("changepattern/cpee1:description/*", namespaces=self.ns))
                label = R_RPST.get_label(etree.tostring(root)).lower()
                roles = R_RPST.get_allowed_roles(etree.tostring(root))
                
                if not (R_RPST.get_label(etree.tostring(root).lower()) == profile.attrib["task"].lower() and (profile.attrib["role"] in R_RPST.get_allowed_roles(etree.tostring(root)) if len(R_RPST.get_allowed_roles(etree.tostring(root))) > 0 else True)):
                    resource.remove(profile)
            
            # Add Resource if it has fitting profiles
            if len(resource.xpath("*")) > 0:
                root.xpath("cpee1:children", namespaces=self.ns)[0].append(resource)

        # End condition for recursive call
        task_elements = R_RPST.CpeeElements().task_elements

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
        
        # Add next tasks to the tree
        for profile in root.xpath("cpee1:children/resource/resprofile", namespaces=self.ns):
            ex_branch = excluded
            if len(profile.xpath("changepattern")) > 0:
                for change_pattern in profile.xpath("changepattern"):
                    #print("CP_kids: ", change_pattern.xpath(".//*", namespaces=self.ns))
                    testy = change_pattern.xpath(".//*")
                    #print(testy[3] in task_elements)
                    #print(testy[3], task_elements[0])
                    cp_tasks = [element for element in change_pattern.xpath(".//*") if element.tag in task_elements]
                    cp_task_labels = [R_RPST.get_label(etree.tostring(task)) for task in cp_tasks]
                    
                    #TODO excluded tasks
                    if any(x['label'].lower() in map(lambda d: d["label"].lower(), cp_task_labels) for x in ex_branch): 
                        print(f"Break reached, task {cp_task_labels} in excluded")
                        root.xpath("cpee1:children/resource/resprofile").remove(profile)
                        break

                    for task in cp_tasks:
                        if len(change_pattern.xpath("@type")[0].lower()) > 0:
                            task.attrib["type"] = change_pattern.xpath("@type")[0].lower()
                        if len(change_pattern.xpath("parameters/direction")) > 0:
                            task.attrib["direction"] = change_pattern.xpath("parameters/direction")[0].text.lower()

                        if change_pattern.xpath("@type")[0].lower() in ["insert", "replace"]:
                            #print("CP_kids: ", change_pattern.xpath(".//*", namespaces=self.ns))
                            profile.xpath("children")[0].append(self.allocate_task(task, resource_url, excluded=ex_branch))

                        elif change_pattern.xpath("@type")[0].lower() == "delete":
                            self.lock = True
                            """
                            TODO Handle Delete: 
                            - end branch here
                            - check if to delete is available in this branch
                            --> run method delete_task in parent class
                            - check if its available to delete in process
                            - if no delete availble: delete Resource profile and maybe resource!
                            """

                            profile.xpath("children")[0].append(task)
                            self.open_delete = True
                            #profile.add_child(self.allocate_task(task, resource_url, excluded=ex_branch, task_parent=root, res_parent=profile))

                        else:
                            raise("Changepattern type not in ['insert', 'replace', 'delete']")
        
        return root
        

class ResourceError(Exception):
    # Exception is raised if no sufficiant allocation for a task can be found for available resources
    
    def __init__(self, task, message="{} No valid resource allocation can be found for the given set of available resources"):
        self.task = task
        self.message = message.format(self.task.label)
        super().__init__(self.message)

class ResourceWarning(UserWarning):
    pass