from lxml import etree

from src.allocation import utils
import numpy as np


class Solution():
    def __init__(self, process,process_allocation, ra_pst):

        self.process = process
        self.process_allocation = process_allocation
        self.ra_pst = etree.fromstring(ra_pst)
        self.invalid_branches = False #rename to "is_valid"
        self.is_final = False
        self.allocated_branches = []
        self.ns = {"cpee1" : list(process.nsmap.values())[0], "allo": "http://cpee.org/ns/allocation"}
        self.task_list = self.process.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns)
        self.tasks_iter = iter(self.task_list) # iterator
        self.delay_deletes = []

    def get_measure(self, measure, operator=sum, flag=False):
        """Returns 0 if Flag is set wrong or no values are given, does not check if allocation is valid"""
        # TODO: Namespace is wrong
        if flag:
            values = self.process.xpath(f".//allo:allocation/cpee1:resource/cpee1:resprofile/cpee1:measures/cpee1:{measure}", namespaces=self.ns)
        else:
            values = self.process.xpath(f".//allo:allocation/resource/resprofile/measures/{measure}", namespaces=self.ns)
        return operator([float(value.text) for value in values])

    def check_validity(self):
        #TODO Expand to also check if same resource is allocated in a parallel branch
        self.process = etree.fromstring(etree.tostring(self.process))
        tasks = self.process.xpath("//*[self::cpee1:call or self::cpee1:manipulate][not(ancestor::cpee1:changepattern) and not(ancestor::cpee1:allocation)and not(ancestor::cpee1:children)]", namespaces=self.ns)

        for task in tasks:
            a = task.xpath("cpee1:allocation/*", namespaces=self.ns)
            with open("text.xml", "wb") as f:
                f.write(etree.tostring(task))
            if not task.xpath("cpee1:allocation/*", namespaces=self.ns):
                self.invalid_branches=True
                break
            #else:
            #    self.invalid_branches=False

    def apply_branches(self, branches:list):
        
        # TODO Testen und checken!
        for branch_no in branches:      
            task = utils.get_next_task(self.tasks_iter, self) # gets next tasks and checks for deletes
            if task == "end":
                for branch, task in self.delay_deletes:
                    if self.process.xpath(f"//*[@id='{task.attrib['id']}'][not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation) and not(ancestor::RA_RPST)]", namespaces=self.ns):
                        self.process = branch.apply_to_process(self.process, solution=self) # apply delays

            allocation = self.process_allocation.allocations[task.attrib['id']] # get allocation
            branch = allocation.branches[branch_no] # get actual branch as R-RPST

            if branch.node.xpath("//*[@type='delete']"):
                self.delay_deletes.append((branch, task))
            else:
                self.process = branch.apply_to_process(self.process, solution=self) # build branch
    
    def get_possible_branches(self):
        branches_list = []
        for task in self.ra_pst.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children) and not(ancestor::cpee1:allocation)]", namespaces=self.ns):
            possible_branches = task.xpath("cpee1:children/*", namespaces=self.ns)
            branches_list.append(len(possible_branches))

        return branches_list