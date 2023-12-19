from lxml import etree
from tree_allocation.tree import R_RPST
import copy

class ChangeOperation():
    
    def get_proc_task(self, process, core_task):
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        proc_tasks = process.xpath(f"//*[@id='{core_task.attrib['id']}']")
        if len(proc_tasks) != 1:
            proc_tasks = list[filter(lambda x: R_RPST.get_label(core_task)== R_RPST.get_label(x), proc_tasks)]
            if len(proc_tasks) != 1:
                raise("Task identifier + label is not unique")

        return proc_tasks[0]



class Insert(ChangeOperation):
    def apply(self, process:etree.Element, core_task:etree.Element, task:etree.Element):
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        core_task = task.xpath("/*")[0]
        proc_task= self.get_proc_task(process, core_task)

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
                proc_task_parent.replace(proc_task, new_parent)

        return process

class Delete(ChangeOperation):
    # TODO Delete is in v01 handled like an insert
    def apply(self, process:etree.Element, core_task:etree.Element, task:etree.Element):
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        core_task = task.xpath("/*")[0]
        proc_task= self.get_proc_task(process, core_task)

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

                proc_task_parent.replace(proc_task, new_parent)
            
        return process
    
class Replace(ChangeOperation):
    def apply(self, process, core_task, task):

        core_task = task.xpath("/*")[0]
        proc_task= self.get_proc_task(process, core_task)
        path = etree.ElementTree(process).getpath(proc_task)
        proc_task.xpath("parent::*")[0].replace(proc_task, task)

        return process

    def apply_delete(): 
        pass

def ChangeOperationFactory(process, core_task, task, cptype):
    localizer =  {
        "insert": Insert().apply,
        "replace": Replace().apply,
        "delete": Delete().apply
    }
    return localizer[cptype](process, core_task, task)