from src.allocation.branch import Branch

from lxml import etree
import random
import copy


class Reinforcement():
    def __init__(self, process_allocation, environment, agent):
        self.env = environment
        self.agent = agent
    

class JobShopEnv():
    def __init__(self, ra_pst, schedule={}):
        self.ra_pst_xml = etree.tostring(ra_pst)
        self.ra_pst_et = ra_pst
        self.schedule = schedule  # Holds information on existing schedule situation, all allocated tasks to machines
        self.current_step = 0

        self.ns = {"cpee1" : list(self.ra_pst_et.nsmap.values())[0], "ra_rpst" : "http://cpee.org/ns/ra_rpst"}
        self.task_list = self.ra_pst_et.xpath("//cpee1:call|//cpee1:manipulate", namespaces=self.ns)

    def add_task_to_schedule(self):
        #TODO: Adds a task with its expected execution time to schedule
        pass

    def reset(self):
        #TODO: reset state
        pass

    def get_state(self):
        #TODO: 
        # returns the current state of the Environment
        # must probably return schedule & "unscheduled RA-PST"
        #
        pass

    def step(self, action=None):
        #TODO: 
        # Decides on Konfiguration and schedules it into Schedule
        # updates the State 
        if self.current_step > len(self.task_list):
            print("done")
            # TODO: 
            # return current state (Schedule)
            # return konfigured process model (CPEE Tree)
            # return done

        else:
            # for now, choose random branch
            current_task = copy.deepcopy(self.task_list[self.current_step])
            branches = current_task.xpath("children/*", namespaces= self.ns) # get branches of RA-PST
            #branches = current_task.xpath("cpee1:children/*", namespaces= self.ns) # get branches of RA-PST
            branch_no = random.randint(0, len(branches)-1)
            branch = etree.Element("children")
            branch.append(branches[branch_no])

            for child in current_task.xpath("*"):
                current_task.remove(child)
            current_task.append(branch)

            
            branch = Branch(current_task)
            finished = branch.apply_to_process(self.ra_pst_et)
            with open("test.xml", "wb") as f:
                f.write(etree.tostring(finished))


            # TODO: choose branch with reinforcement learn "action"
        print("done2")

    def calculate_makespan(self):
        #TODO:
        # calculate overall makespan
        pass

    def print_schedule(self):
        #TODO: 
        # Print Schedule 
        pass 


