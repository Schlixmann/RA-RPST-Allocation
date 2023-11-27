from tree_allocation.tree import task_node as tn
from tree_allocation.tree import res_node as rn
from tree_allocation.helpers import get_all_resources, get_all_tasks, get_process_model
from tree_allocation.allocation.change_operations import *

from PrettyPrint import PrettyPrintTree
from tree_allocation.proc_resource import *
from lxml import etree
import warnings
import logging
logger = logging.getLogger(__name__)

ns = {"cpee2": "http://cpee.org/ns/properties/2.0", 
        "cpee1":"http://cpee.org/ns/description/1.0"}

class TaskAllocation():

    def __init__(self, task, xml_str, state=None, ) -> None:
        allowed_states = {'ready', 'running', 'stopped', 'finished', 'initialized'}

        self.id = str(uuid.uuid1())
        self.task = task
        self.state = state
        self.allo_tree = None
        self.xml_str = xml_str

    def allocate_task(self):
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



def parse_tasks(xml_string:str):
    ns = {"cpee2": "http://cpee.org/ns/properties/2.0", 
        "cpee1":"http://cpee.org/ns/description/1.0"}
    #parsed = etree.fromstring(xml_string)
    parsed = xml_string
    tasks = []
    roles = []

    for task in parsed.xpath(".//cpee1:call | .//cpee1:manipulate", namespaces=ns):
        if task.tag == etree.QName(ns["cpee1"], "manipulate"):
            # TODO: add for call type: Label is stored as parameter
            task_id = task.attrib["id"]
            roles = [role.text for role in task.findall(".//cpee1:resource", ns)]
            label = task.attrib["label"]

        else: 
            task_id = task.attrib["id"]
            roles = [role.text for role in task.findall(".//cpee1:resource", ns)]
            label = task.find(".//cpee1:parameters/cpee1:label", ns).text
        tasks.append({"task_id": task_id, "label": label, "roles": roles})
    return tasks

def build_allo_tree(root, av_resources:Resource=[], excluded=[], task_parent=None, res_parent=None):
    # TODO: Multiple RP's for one resource where one RP is not possible must be created still.
    
    for resource in av_resources:
        for profile in resource.resource_profiles:
            if root.label.lower() == profile.task.lower() and (profile.role in root.allowed_roles if len(root.allowed_roles) > 0 else True): 
                root.add_child(rn.ResourceNode(resource, resource.name, profile, profile.task, profile.measure))

    if len(root.children) == 0:
        if not task_parent:
            warnings.warn("No resource for a core task")
            raise(ResourceError(root))
        # TODO Attribute error does not happen, situation is not cancelled
        task_parent.children = [task for task in task_parent.children if task.resource_profile != res_parent.resource_profile]
        if len(task_parent.children) == 0:
            warnings.warn("The task can not be allocated due to missing resource availability", ResourceWarning)
            raise(ResourceError(task_parent))
        
        return root
        
    
    for resource in root.children:
        ex_branch = excluded
        if len(resource.resource_profile.change_patterns) > 0:
            for change_patterns in resource.resource_profile.change_patterns:

                tasks = parse_tasks(change_patterns)
                #print(ex_branch , "and \n ", tasks)
                if any(x['label'].lower() in map(lambda d: d["label"].lower(), tasks) for x in ex_branch): 
                    print(f"Break reached, task {tasks} in excluded")
                    root.children.remove(resource)
                    break

                for task in tasks:
                    ex_branch = ex_branch + [task]
                    task = tn.TaskNode(task["task_id"], task["label"], allowed_roles=task["roles"])
                    resource.add_child(build_allo_tree(task, av_resources, excluded=ex_branch, task_parent=root, res_parent=resource))
                
    return root

def allocate_process(cpee_url, resource_url="http://127.0.0.1:8000/resources", measure=None, operator=min, file_path:str = "res_config_cost3"):
    #resources = get_all_resources("./config/res_config_5.xml")
    resources = get_all_resources(resource_url, file_path)
    logger.info(f"Test logging from module {[r.name for r in resources]}")
    process_model_xml, process_model_etree = get_process_model(cpee_url)
    tasklabels = []
    for task in get_all_tasks(cpee_url):
        try:
            tasklabels.append({"task_id": task.attrib["id"] ,"label": task.attrib["label"]})
            
        except:
            try:
                attrib = task.find(".//cpee1:parameters", ns)
                if not attrib.find(".//cpee1:label", ns).text:
                     raise Exception("Task {} has no label.".format(task.attrib["id"]))
                else:
                     tasklabels.append({"task_id": task.attrib["id"], "label": attrib.find(".//cpee1:label", ns).text })
            except Exception as e:
                print(e)
                continue
    print("Tasklabels: ", tasklabels)
    print("Resource: ", resources)

    
    
    i = 0
    for task in tasklabels:
        print(f"Start Allocation of {task}")
        root = tn.TaskNode(task["task_id"], task["label"])
        try:
            build_allo_tree(root, resources)
            #print_allo_tree(root)

            pt = PrettyPrintTree(lambda x: x.children, lambda x: "task:" + str(x.label) + " " + str(x.id) if type(x) == tn.TaskNode else "res:" + str(x.name) + " rp:" + str(x.resource_profile.name) + f"\n {str(measure)}: "  + str(x.measure[measure]))
            pt(root)

            
            best_branch, branch_measure, value, best_node = root.get_best_branch(measure=measure, operator=operator)
            print("Best_branch", f"All branch measures: {branch_measure}, best measure: {value}")
            pt(best_node)
            # TODO: create change operation

            all_resources = best_node.get_all_nodes()
            print([resource.get_name for resource in all_resources])

            process_model_xml, changed_model_etree = create_change_operation(best_node, process_model_xml)
            
            with open(f"./output/out_{str(i)}.xml", "wb") as f:
                f.write((process_model_xml))

            logger.info(f"Task successfully allocate: {root.get_name}")
        except ResourceError as e:
            e.add_note(f"No allocation possible, the task: {task} is skipped")
            print("Task not allocatable:", e.task.get_name, ", Message:", e.message)
            
        #except Exception as e:
        #    print("Allocation Failed")
        #    print(e)
            
        i += 1
        
        
    with open("./output/test.xml", "wb") as f:
        f.write((process_model_xml))
    return process_model_xml

class ResourceError(Exception):
    # Exception is raised if no sufficiant allocation for a task can be found for available resources
    
    def __init__(self, task, message=f"No valid resource allocation can be found for the given set of available resources"):
        self.task = task
        self.message = message
        super().__init__(self.message)

class ResourceWarning(UserWarning):
    pass
# TODO 
# 1. get allocation for each task. 
# 2. build change operations for this task
# 3. Integrate change operations in original RPST
# 4. Make accessible and return to CPEE
