from lxml import etree
from tree_allocation.tree import R_RPST
import copy
import re


class ChangeOperation():
    def get_proc_task(self, process, core_task):
        with open("xml_out2.xml", "wb") as f:
            f.write(etree.tostring(process))
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        proc_tasks = process.xpath(f"//*[@id='{core_task.attrib['id']}'][not(ancestor::changepattern)]", namespaces=ns)
        if len(proc_tasks) != 1:
            proc_tasks = list(filter(lambda x: R_RPST.get_label(etree.tostring(core_task))== R_RPST.get_label(etree.tostring(x)), proc_tasks))
            if len(proc_tasks) > 1:
                raise ProcessError(f"Task identifier + label is not unique for task {R_RPST.get_label(etree.tostring(core_task)), core_task.attrib}")
            elif len(proc_tasks) == 0:
                raise ProcessError(f"Task identifier + label do not exist {R_RPST.get_label(etree.tostring(core_task)), core_task.attrib}")
        return proc_tasks[0]

    def add_res_allocation(self, task, output):
        ns = {"cpee1" : list(task.nsmap.values())[0]}
        if not task.xpath("cpee1:allocation", namespaces=ns):
            task.xpath(".")[0].append(etree.Element(f"{{{ns['cpee1']}}}allocation"))
        #task.xpath("cpee1:allocation", namespaces=ns)[0].append(etree.Element(f"{{{ns['cpee1']}}}res_allocation"))
        #with open("res2_xml.xml", "wb") as f:
        #    f.write(etree.tostring(output))
        set_allocation = output.xpath("@name")[0] + " role: " + output.xpath("*/@role")[0]  + output.xpath("*/@id")[0]  # add ID
        task.xpath("cpee1:resources", namespaces=ns)[0].set("allocated_to", set_allocation)
        task.xpath("cpee1:allocation", namespaces=ns)[0].append(output)
    
    def get_next_task_id(self, process):
        # create unique task_id
        rt_ids = process.xpath("//@id")
        pattern = re.compile(r'rp|r_|a')
        try:
            curr_rp_id = max([int(re.split("\\D", id)[-1]) for id in rt_ids if not pattern.search(id)])
        except ValueError:
            #print("Curr_rp_id starting at 0")
            curr_rp_id = 0
        #print("Curr Id:", curr_rp_id)
        return str(curr_rp_id + 1)
        

class Insert(ChangeOperation):
    def apply(self, process:etree.Element, core_task:etree.Element, task:etree.Element):
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        invalid = False
        process = copy.deepcopy(process)
        #core_task = task.xpath("/*")[0]
        proc_task= self.get_proc_task(process, core_task)



        # create next id for task to insert (changed in branch as well!)
        task.attrib["id"] = "r"+self.get_next_task_id(process)
        task = copy.deepcopy(task)
        try:
            if task.xpath("cpee1:children/*", namespaces=ns):
                resource_info = copy.deepcopy(task.xpath("cpee1:children/*", namespaces=ns)[0])
                self.add_res_allocation(task, resource_info)
            else: 
                raise ChangeOperationError("No Resource available. Invalid Allocation")
        except ChangeOperationError as inst:
            #print(inst.__str__())
            invalid = True

        match task.attrib["direction"]:
            case "before":
                proc_task.addprevious(task)
            case "after":
                proc_task.addnext(task)
            case "parallel":
                proc_task_parent = proc_task.xpath("parent::*")[0]
                new_parent = R_RPST.CpeeElements().parallel()
                new_parent.xpath("cpee1:parallel_branch", namespaces=ns)[0].append(copy.deepcopy(proc_task))
                new_parent.xpath("cpee1:parallel_branch", namespaces=ns)[1].append(task)
                proc_task.addnext(new_parent)
                proc_task_parent.remove(proc_task)

        return process, invalid
    
class Delete(ChangeOperation):
    # TODO Cascade delete of allocations
    # TODO if DELETE is only task in a parallel/ choose branch, full parallel must be deleted

    def apply(self, process:etree.Element, core_task:etree.Element, task:etree.Element):
        invalid = False
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        with open("xml_out3.xml", "wb") as f:
            f.write(etree.tostring(process))
        #proc_task= self.get_proc_task(process, core_task)
        proc_task = 1
        match task.attrib["direction"]:
            case "before":
                # TODO: 
                # Check if Task is in previous of process
                # Delete Task from Process Tree
                proc_task.addprevious(task)
            case "after":
                # TODO: 
                # Check if Task is in following of process
                # Delete Task from Process Tree

                proc_task.addnext(task)
            case "parallel":
                # TODO: 
                # Check if Task is in following of process
                # Delete Task from Process Tree
                proc_task_parent = proc_task.xpath("parent::*")[0]
                new_parent = R_RPST.CpeeElements().parallel()
                new_parent.xpath("cpee1:parallel_branch", namespaces=ns)[0].append(copy.deepcopy(proc_task))
                new_parent.xpath("cpee1:parallel_branch", namespaces=ns)[1].append(copy.deepcopy(task))

                proc_task_parent.append(new_parent)

            case "any":
                # TODO: 
                # Check if Task is in process
                # Delete Task from Process Tree
                proc = process.xpath(f"//*[not(ancestor::changepattern) and not(ancestor::cpee1:allocation) and not(ancestor::cpee1:children)]", namespaces=ns)
                labels = []

                try:
                    to_del_label = R_RPST.get_label(etree.tostring(task)).lower()
                except TypeError as inst:
                    print(inst.__str__())
                    print("The Element Tag of the task is {}".format(inst.args[1]))

                pos_deletes = []
                for x in proc: 
                    try: 
                        if to_del_label == R_RPST.get_label(etree.tostring(x)).lower():
                            pos_deletes.append(x.xpath("@id", namespaces=ns)[0])

                    except TypeError as inst:
                        #print(inst.__str__())
                        pass
                try:
                    if pos_deletes:
                        to_del_id = pos_deletes[0]
                        with open("xml_out", "wb") as f:
                            f.write(etree.tostring(proc[0]))
                    else:
                        raise ChangeOperationError("No matching task to delete found in Process Model")
                
                except ChangeOperationError as inst:
                    #print(inst.__str__())
                    invalid = True
                    return process, invalid 

                to_dels = process.xpath(f"//*[@id='{to_del_id}'][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)and not(ancestor::cpee1:children)]", namespaces=ns)

                #TODO Delete Cascade: if to_del has change patterns in allocation, they need to be deleted as well. 
                to_del = to_dels[0]
                to_del_parent = to_del.xpath("parent::*")[0]
                to_del_parent.remove(to_del)


                # Delete Cascade:
                for to_del2 in to_del.xpath("cpee1:allocation/resource/resprofile/cpee1:children/*", namespaces=ns):
                    to_del2.attrib["type"], to_del2.attrib["direction"] = task.attrib["type"], task.attrib["direction"]
                    process, invalid = Delete().apply(process, core_task, to_del2)

        return process, invalid

def print_node_structure(ns, node, level=0):
    if node.tag==f"{{{ns['cpee1']}}}manipulate": print('  ' * level + node.tag + ' ' + str(node.attrib), node )
    for child in node.xpath("*"):
        print_node_structure(ns, child, level + 1)
    
class Replace(ChangeOperation):
    def apply(self, process, core_task, task):
        invalid = False
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        proc_task= self.get_proc_task(process, core_task)
        task.attrib["id"] = "r" + self.get_next_task_id(process)

        #proc_task = self.get_proc_task(process, to_replace)
        proc_task.xpath("parent::*")[0].replace(proc_task, task)

        try:
            if task.xpath("cpee1:children/*", namespaces=ns):
                resource_info = copy.deepcopy(task.xpath("cpee1:children/*", namespaces=ns)[0])
                self.add_res_allocation(task, resource_info)
            else: 
                raise ChangeOperationError(f"No Resource available for replaced {R_RPST.get_label(etree.tostring(task))}. Invalid Allocation")
        
        except ChangeOperationError as inst:
            #print(inst.__str__())
            invalid = True

        return process, invalid

class ChangeOperationError(Exception):
    "Raised when an Error Occurs during application of a change operation"
    pass

class ResourceAllocationError(Exception):
    "Raised when no fitting resource is available"
    pass

class ProcessError(Exception):
    "Raised when no fitting resource is available"
    pass

def ChangeOperationFactory(process, core_task, task, cptype):
    localizer =  {
        "insert": Insert().apply,
        "replace": Replace().apply,
        "delete": Delete().apply
    }
    return localizer[cptype](process, core_task, task)

