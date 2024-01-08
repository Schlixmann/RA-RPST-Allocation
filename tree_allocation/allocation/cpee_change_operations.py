from lxml import etree
from tree_allocation.tree import R_RPST
import copy

class ChangeOperation():
    def get_proc_task(self, process, core_task):
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        proc_tasks = process.xpath(f"//*[@id='{core_task.attrib['id']}'][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ns)
        if len(proc_tasks) != 1:
            proc_tasks = list(filter(lambda x: R_RPST.get_label(etree.tostring(core_task))== R_RPST.get_label(etree.tostring(x)), proc_tasks))
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
                new_parent.xpath("cpee1:parallel_branch", namespaces=ns)[0].append(proc_task)
                new_parent.xpath("cpee1:parallel_branch", namespaces=ns)[1].append(task)
                proc_task_parent.append(new_parent)

        return process

class Delete(ChangeOperation):
    # TODO Delete is in v01 handled like an insert
    def apply(self, process:etree.Element, core_task:etree.Element, task:etree.Element):
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        core_task = task.xpath("/*")[0]
        proc_task= self.get_proc_task(process, core_task)

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
                new_parent.xpath("cpee1:parallel_branch", namespaces=ns)[0].append(proc_task)
                new_parent.xpath("cpee1:parallel_branch", namespaces=ns)[1].append(task)

                proc_task_parent.append(new_parent)

            case "any":
                # TODO: 
                # Check if Task is in process
                # Delete Task from Process Tree
                proc = process.xpath(f"//*[not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ns)
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
                        print(inst.__str__())
                        pass
                if pos_deletes:
                    to_del_id = pos_deletes[0]
                else:
                    raise ChangeOperationError("No matching task to delete found in Process Model")


                to_del = process.xpath(f"//*[@id='{to_del_id}'][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ns)[0]
                process.remove(to_del)

            
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

class ChangeOperationError(Exception):
    "Raised when an Error Occurs during application of a change operation"
    pass


def ChangeOperationFactory(process, core_task, task, cptype):
    localizer =  {
        "insert": Insert().apply,
        "replace": Replace().apply,
        "delete": Delete().apply
    }
    return localizer[cptype](process, core_task, task)

