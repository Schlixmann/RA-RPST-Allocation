from tree_allocation.allocation import cpee_change_operations


from lxml import etree


import copy


class Branch():
    def __init__(self, node):
        self.node = node
        self.valid = True
        self.open_delete = False
        self.current_path = ''

    #TODO Calculate costs of Branch --> needed for heuristical decision
    def get_measure(self, measure, operator=sum):
        "Calculate the measure for one Branch"
        ns = {"cpee1" : list(self.node.nsmap.values())[0]}
        #TODO should calculate the sum of the measure for the branch
        # For one allocation the best bracnch should then be found (or best 2,3,4 etc)
        #with open("xml_out.xml", "wb") as f:
        #    f.write(etree.tostring(self.node))
        values = self.node.xpath(f".//cpee1:children/resource/resprofile/measures/{measure}", namespaces=ns)
        return operator([float(value.text) for value in values])
        pass

    def apply_to_process(self, process, solution=None, next_task=None) -> etree:
        #TODO should be part of "Branch"
        """
        -> Find task to allocate in self.process
        -> apply change operations
        """
        ns = {"cpee1" : list(process.nsmap.values())[0]}
        with open("branch_raw.xml", "wb") as f:
            f.write(etree.tostring(self.node))
        #TODO Set allocated Resource!

        tasks = copy.deepcopy(self.node).xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::changepattern) and not(ancestor::cpee1:changepattern)and not(ancestor::cpee1:allocation)]", namespaces=ns)[1:]
        #TODO This does it work for branches with more than 2 levels?


        dummy = cpee_change_operations.ChangeOperation()
        task = dummy.get_proc_task(process, copy.deepcopy(self.node))
        if self.node.xpath("cpee1:children/*", namespaces=ns):
            poop = copy.deepcopy(self.node.xpath("cpee1:children/*", namespaces=ns)[0])
            to_del = poop.xpath("cpee1:resource/cpee1:resprofile/cpee1:children", namespaces=ns)
            if to_del:
                resource_info = poop.xpath("cpee1:resprofile", namespaces=ns)[0].remove(to_del)
            resource_info = poop
            dummy.add_res_allocation(task, resource_info)

        for task in tasks:
            try:
                anchor = task.xpath("ancestor::cpee1:manipulate | ancestor::cpee1:call", namespaces=ns)[-1]
                process, solution.invalid_branches = cpee_change_operations.ChangeOperationFactory(process, anchor, task, cptype= task.attrib["type"])
                #resource_info = copy.deepcopy(core_task.xpath("cpee1:children/*", namespaces=ns)[0])
                    
                #graphix.TreeGraph().show(etree.tostring(self.node), filename=f"branch") 

            except cpee_change_operations.ChangeOperationError as inst:
                solution.invalid_branches = True
                #print(inst.__str__())
                #print("Solution invalid_branches = True")

        return process