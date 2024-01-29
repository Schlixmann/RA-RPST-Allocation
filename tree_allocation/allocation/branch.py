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
        #TODO Set allocated Resource!

        tasks = copy.deepcopy(self.node).xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::changepattern) and not(ancestor::cpee1:allocation)]", namespaces=ns)[1:]
        #TODO This does it work for branches with more than 2 levels?

        #with open("branch.xml", "wb") as f:
        #    f.write(etree.tostring(self.node))

        dummy = cpee_change_operations.ChangeOperation()
        task = dummy.get_proc_task(process, copy.deepcopy(self.node))
        if self.node.xpath("cpee1:children/*", namespaces=ns):
            poop = copy.deepcopy(self.node.xpath("cpee1:children/*", namespaces=ns)[0])
            to_del = poop.xpath("cpee1:resource/cpee1:resprofile/cpee1:children", namespaces=ns)
            if to_del:
                resource_info = poop.xpath("cpee1:resprofile", namespaces=ns)[0].remove(to_del)
            resource_info = poop
            with open("res_xml.xml", "wb") as f:
                f.write(etree.tostring(poop))

            dummy.add_res_allocation(task, resource_info)

        for task in tasks:
            try:
                core_task = copy.deepcopy(task.xpath("ancestor::*[self::cpee1:manipulate|self::cpee1:call]", namespaces=ns)[0])
                i = 0
                if i == 1:
                    with open("xml_out.xml", "wb") as f:
                        f.write(etree.tostring(process))

                process = cpee_change_operations.ChangeOperationFactory(process, core_task, task, cptype= task.attrib["type"])
                resource_info = copy.deepcopy(core_task.xpath("cpee1:children/*", namespaces=ns)[0])
                with open("branch.xml", "wb") as f:
                    f.write(etree.tostring(self.node))
                #graphix.TreeGraph().show(etree.tostring(self.node), filename=f"branch") 

            except cpee_change_operations.ChangeOperationError as inst:
                solution.invalid_branches = True
                #print(inst.__str__())
                #print("Solution invalid_branches = True")

        #open("xml_out2.xml", "wb").write(etree.tostring(process))
        return process