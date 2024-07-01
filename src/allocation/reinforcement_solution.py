from src.allocation.branch import Branch
from src.allocation.solution import Solution
from src.allocation.utils import get_next_task

from lxml import etree
import random
import copy
from collections import defaultdict

class Reinforcement():
    def __init__(self, process_allocation, environment, agent):
        self.env = environment
        self.agent = agent
    

class JobShopEnv():
    def __init__(self, ra_pst, schedule=defaultdict(list)):
        self.ra_pst_xml = ra_pst
        self.ra_pst_et = etree.fromstring(ra_pst)
        self.schedule = schedule  # Holds information on existing schedule situation, all allocated tasks to machines
        self.current_step = 0 
        self.solution = Solution(self.ra_pst_et)
        self.final_config = None

        self.ns = {"cpee1" : list(self.ra_pst_et.nsmap.values())[0], "ra_rpst" : "http://cpee.org/ns/ra_rpst"}
        self.task_list = copy.deepcopy(self.ra_pst_et.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children)]", namespaces=self.ns))
        self.tasks_iter = copy.copy(iter(self.task_list)) # iterator

    def add_task_to_schedule(self, task):
        #TODO: Adds a task with its expected execution time to schedule
        with open("task.xml","wb") as f:
            f.write(etree.tostring(task))
        
        task = etree.fromstring(etree.tostring(task))
        resources = task.xpath("cpee1:allocation/cpee1:resource", namespaces=self.ns)
        if resources: 
            resource = resources[0].attrib["id"]
            task_id = task.attrib["id"]
            time = float(task.xpath("cpee1:allocation/cpee1:resource/cpee1:resprofile/cpee1:measures/cpee1:cost", namespaces=self.ns)[0].text)
            if self.schedule[resource]:
                start_time = self.schedule[resource][-1]["start"]+self.schedule[resource][-1]["duration"]
            else:
                start_time = 0
            self.schedule[resource].append({"task":task_id, "duration":time, "start":start_time})
        else:
            raise ValueError(f"No resource found for task_id {task.attrib["id"]}")
        return self.schedule

    def reset(self):
        #TODO: reset state
        pass

    def get_state(self):
        #TODO: 
        # returns the current state of the Environment
        # must probably return schedule & "unscheduled RA-PST"
        #
        return 0

    def step(self, action=None):
        #TODO: 
        # Decides on Konfiguration and schedules it into Schedule
        # updates the State 

        task = get_next_task(self.tasks_iter, self.solution)
        if task == "end":
            self.reload_etree()
            print("Etrees are the same: ", etree.tostring(self.final_config) == etree.tostring(self.ra_pst_et))
            if True: # TODO: toggle if dynamic scheduling during config or after config is finished
                # TODO: create schedule for fully configured process
                to_schedule_list = copy.deepcopy(self.final_config.xpath("(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children or ancestor::cpee1:allocation)]", namespaces=self.ns))
                for task in to_schedule_list:
                    self.add_task_to_schedule(task)
                print("done")
                done = True
                return done, self.final_config, self.schedule
            # return current state (Schedule)
            # return konfigured process model (CPEE Tree)
            # return done

        else:
            # for now, choose random branch
            current_task = task
            with open("test.xml", "wb") as f:
                f.write(etree.tostring(current_task))
            branches = current_task.xpath("cpee1:children/*", namespaces= self.ns) # get branches of RA-PST
            #branches = current_task.xpath("cpee1:children/*", namespaces= self.ns) # get branches of RA-PST
            self.print_node_structure(current_task)
            branch_no = random.randint(0, len(branches)-1)
            branch = etree.Element(f"{{{self.ns["cpee1"]}}}children")
            branch.append(branches[branch_no])

            for child in current_task.xpath("cpee1:children", namespaces=self.ns):
                current_task.remove(child)
            current_task.append(branch)

            
            branch = Branch(current_task)
            self.final_config = branch.apply_to_process(self.ra_pst_et, self.solution)
            with open("test.xml", "wb") as f:
                f.write(etree.tostring(self.final_config))
            # TODO: choose branch with reinforcement learn "action"
            # TODO: Get only the newly allocated tasks and schedule during Configuration

            # TODO: Scheduling

            self.current_step += 1
        

        return None, None, None

    def calculate_makespan(self):
        #TODO:
        # calculate overall makespan
        pass

    def print_schedule(self):
        #TODO: 
        # Print Schedule 
        pass 

    def print_node_structure(self, node, level=0):
        """
        Prints structure of etree.element to cmd
        """
        print('  ' * level + node.tag + ' ' + str(node.attrib))
        for child in node.xpath("*"):
            self.print_node_structure(child, level + 1)
    
    def reload_etree(self):
        self.final_config = etree.fromstring(etree.tostring(self.final_config))


