from tree_allocation.tree import task_node as tn
from tree_allocation.tree import res_node as rn, R_RPST
from tree_allocation.helpers import get_all_resources, get_all_tasks, get_process_model
from tree_allocation.allocation.change_operations import *

from PrettyPrint import PrettyPrintTree
from tree_allocation.proc_resource import *
from lxml import etree
import warnings
import logging
import copy
logger = logging.getLogger(__name__)



class TaskAllocation():

    def __init__(self, process, task, state='initialized', ) -> None:
        allowed_states = {'ready', 'running', 'stopped', 'finished', 'initialized'}

        self.id = str(uuid.uuid1())
        self.task = task
        self.state = state
        self.final_tree = None
        self.intermediate_trees = []
        self.process = process
        self.lock:bool = False
        self.ns = None

    def allocate_task(self, root=None, resource_url = None, excluded=[]):
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
                print("Profile description: ", profile.xpath("changepattern/cpee1:description/*", namespaces=self.ns))
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
                    print("CP_kids: ", change_pattern.xpath(".//*", namespaces=self.ns))
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
                            print("CP_kids: ", change_pattern.xpath(".//*", namespaces=self.ns))
                            profile.xpath("children")[0].append(self.allocate_task(task, resource_url, excluded=ex_branch))

                        elif change_pattern.xpath("@type")[0].lower() == "delete":
                            self.lock = True
                            profile.xpath("children")[0].append(self.allocate_task(task, resource_url, excluded=ex_branch))
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