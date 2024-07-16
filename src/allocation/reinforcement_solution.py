from src.allocation.branch import Branch
from src.allocation.solution import Solution
from src.allocation.utils import *

from lxml import etree
import random
import copy
from collections import defaultdict
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam


class Reinforcement():
    def __init__(self, process_allocation, environment, agent):
        self.env = environment
        self.agent = agent


class JobShopEnv():
    def __init__(self, ra_pst, schedule=defaultdict(dict), current_instance_id=1):
        #self.ra_pst_xml = ra_pst
        self.ra_pst_et = etree.fromstring(ra_pst)
        # Holds information on existing schedule situation, all allocated tasks to machines
        self.schedule = schedule

        self.init_ra_pst_et = copy.deepcopy(self.ra_pst_et)
        self.init_schedule = copy.deepcopy(self.schedule)
        self.current_step = 0
        self.solution = Solution(self.ra_pst_et)
        self.final_config = None
        self.to_delete =[]
        self.valid_solution = []
        self.current_instance_id = current_instance_id

        self.ns = {"cpee1": list(self.ra_pst_et.nsmap.values())[0], "ra_rpst": "http://cpee.org/ns/ra_rpst"}
        self.task_list = copy.deepcopy(self.ra_pst_et.xpath(
            "(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children)]", namespaces=self.ns))
        self.tasks_iter = copy.copy(iter(self.task_list))  # iterator
        self.current_task = get_next_task(self.tasks_iter, self.solution)
        self.current_task_number = 0
        self.all_resources = set(self.ra_pst_et.xpath("//cpee1:children/cpee1:resource/@id", namespaces=self.ns))
    
    def get_next_schedule_id(self):
        highest_id = 0
        for resource, tasks in self.schedule.items():
            for task, values in tasks.items():
                highest_id = max(highest_id, values['id'])
        return highest_id + 1


    def add_task_to_schedule(self, proc_task, label=None):
        # TODO: Ensure precedence rules
        if label in self.to_delete:
            return self.schedule
        
        previous_task = None
        max_task_id = 0
        for resource, tasks in self.schedule.items():
            for task, values in tasks.items():
                if values["instance_id"] == self.current_instance_id and values['id'] > max_task_id:
                    previous_task = tasks[task]
                    max_task_id = values["id"]

        proc_task = etree.fromstring(etree.tostring(proc_task))
        resources = proc_task.xpath("cpee1:allocation/cpee1:resource", namespaces=self.ns)
        if resources:
            # TODO: make attribute independent
            # TODO: set start time on previous task in process
            resource, instance_id, task_id, time = resources[0].attrib["id"], self.current_instance_id, proc_task.attrib["id"], float(proc_task.xpath(
                "cpee1:allocation/cpee1:resource/cpee1:resprofile/cpee1:measures/cpee1:cost", namespaces=self.ns)[0].text)

            # find earliest_possible_start_time
            if previous_task:
                earliest_possible_start_time = previous_task["start"] + previous_task["duration"]
            else: 
                earliest_possible_start_time = 0
            
            earliest_possible_end_time = earliest_possible_start_time + time
            
            if resource in self.schedule.keys():
                # check if earliest possible start time + duration time conflicts with any other task on the resource
                # if yes: earliest_possible_start_time = start_time of conflitcting task + duration of conflicting task
                # if not: add task to schedule @earliest_possible_start_time

                conflict = True
                while conflict: 
                    for task, values in self.schedule[resource].items():
                        if earliest_possible_start_time < values["start"] and earliest_possible_end_time > values["start"]:
                            conflict = True
                            earliest_possible_start_time = values["start"] + values["duration"]
                            earliest_possible_end_time = earliest_possible_start_time + time
                            continue
                        elif earliest_possible_start_time > values["start"] and earliest_possible_start_time < values["start"]+ values["duration"]:
                            conflict = True
                            earliest_possible_start_time = values["start"] + values["duration"]
                            earliest_possible_end_time = earliest_possible_start_time + time
                            continue
                        else:
                            conflict = False

            task_in_config = self.final_config.xpath(f"//*[@id = '{proc_task.attrib['id']}']")[0]
            schedule_id = self.get_next_schedule_id()
            task_in_config.attrib["schedule_id"] = str(schedule_id)

            self.schedule[resource][f"{task_id}_{instance_id}"] = {"task": task_id, 
                 "instance_id":instance_id, "id":schedule_id, "duration": time, "start": earliest_possible_start_time}

        else:
            pass
            #raise ValueError(f"No resource found for task_id {task.attrib["id"]}")
        
        return self.schedule

    def reset(self):
        # TODO: reset state
        self.schedule = self.init_schedule
        self.current_task_number = -1
        self.ra_pst_et = copy.deepcopy(self.init_ra_pst_et)

        self.task_list = copy.deepcopy(self.ra_pst_et.xpath(
            "(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children)]", namespaces=self.ns))
        self.tasks_iter = copy.copy(iter(self.task_list))  # iterator
        self.current_task = get_next_task(self.tasks_iter, self.solution)
        self.current_task_number = 0

        self.solution = Solution(self.ra_pst_et)
        self.final_config = None
        self.to_delete =[]
        self.valid_solution = []

        return self.get_state_aggregation()

    def get_state(self):
        # TODO:
        # returns the current state of the Environment
        # must probably return schedule & "unscheduled RA-PST"
        matrix = np.zeros((len(self.schedule.items()), 100000))
        # Transform Schedule to flat Array: 
        i = 0
        for resource, tasks in self.schedule.items(): 
            for task_id, values in tasks.items():
                start = int(values["start"])
                duration = int(values["duration"])
                end = start + duration
                matrix[i][start:end] = 1
            i += 1

        return matrix.flatten()
    
    def get_state_aggregation(self):
        # Resource Coverage
        # Endtime of last Scheduled item per Resource
        # Resource Coverage per Resource per available branch
        # Task Delta per branch
        self.sort_schedule_by_resource()
        max_last_task = 0
        last_tasks = defaultdict(dict)
        for resource, tasks in self.schedule.items():
            last_task = {"start": 0, "duration":0}
            for task, values in tasks.items():
                if values["start"] > last_task["start"]:
                    last_task = values

            last_task_end = last_task["start"] + last_task["duration"]
            if last_task_end > max_last_task: max_last_task, self.last_task_end = last_task_end, last_task_end

            last_tasks[resource]["last_task"] = last_task
        

        fin_list = np.zeros((2, len(self.all_resources)))
        for resource, values in last_tasks.items():
            last_tasks[resource]["attributes"] = {"coverage": sum(values["duration"] for task, values in self.schedule[resource].items()) / max_last_task}
            fin_list[0][int(str(resource)[-1])-1] = (last_tasks[resource]["attributes"]["coverage"])    
            fin_list[1][int(str(resource)[-1])-1] = float((last_tasks[resource]["last_task"]["start"]+last_tasks[resource]["last_task"]["duration"]))

        state = np.append(fin_list.flatten(), self.current_task_number)
        self.current_task_number += 1
        return state

    def step(self, action=None):

        # TODO:
        # Decides on Konfiguration and schedules it into Schedule
        # updates the State

        task = self.current_task

        # for now, choose random branch
        current_task= task 
        branches = current_task.xpath(
            "cpee1:children/*", namespaces=self.ns)  # get branches of RA-PST
        with open("test.xml", "wb") as f:
            f.write(etree.tostring(current_task))
        
        #TODO: Choose branch based on action
        #   Reward: direct impact + notion on overall validity
        #   Reward: direct impact must come from scheduling
        #   Reward: discount later schedulings
        
        #self.print_node_structure(current_task)
        
        print("Action: ", action)
        et_elem = etree.Element(f"{{{self.ns["cpee1"]}}}children")
        et_elem.append(branches[action])

        # remove existing children to get branch
        for child in current_task.xpath("cpee1:children", namespaces=self.ns):
            current_task.remove(child)
        current_task.append(et_elem)
        branch = Branch(current_task)

        self.final_config = branch.apply_to_process(
            self.ra_pst_et, self.solution)
        
        self.valid_solution.append(self.solution.invalid_branches)
        print(" ")
    


        for task in branch.node.xpath("(//cpee1:manipulate|//cpee1:call)[not(ancestor::cpee1:changepattern)]", namespaces=self.ns):
            # find task in final konfig: 
            #label = task.attrib["label"]
            with open("text.xml", "wb") as f:
                f.write(etree.tostring(branch.node))

            self.reload_etree()
            label = get_label(etree.tostring(task))    
            if ("type","delete") in task.attrib.items():
                # deleted task must not be scheduled
                continue
            
            proc_task = self.final_config.xpath(f"(//cpee1:manipulate[@label='{label}']|//cpee1:call/cpee1:parameters/cpee1:label[text()='{label}']/ancestor::*[2])[not(ancestor::cpee1:children|ancestor::cpee1:allocation)]", namespaces=self.ns)
            if len(proc_task)>1:
                raise ValueError

            self.add_task_to_schedule(proc_task[0], label)
        
        # TODO: choose branch with reinforcement learn "action"
        # TODO: Get only the newly allocated tasks and schedule during Configuration
        #   ->  needed to get immidiate reward. Maybe Identification via label & resource
        # TODO: Set Reward based on Scheduling. Discounting for later decisions!
        #   ->  possibility to get reward + discounted reward?
        # TODO: Scheduling with good scheduler, Scheduling of one allocated task

        self.current_step += 1
        self.current_task = get_next_task(self.tasks_iter, self.solution)
        if self.current_task == "end":
            self.reload_etree()
            print("Etrees are the same: ", etree.tostring(
                self.final_config) == etree.tostring(self.ra_pst_et))
            
            #TODO: Fix all namespace issues
            self.solution.process = etree.fromstring(etree.tostring(self.solution.process))
            self.solution.check_validity()
            self.valid_solution.append("full:")
            self.valid_solution.append(self.solution.invalid_branches)

            print("done")
            done = True
            return self.get_state_aggregation(), self.get_reward(), done, None

        return self.get_state_aggregation(), self.get_reward(), None, self.get_possible_actions()
    
    def get_reward(self):
        return -self.last_task_end

    def get_possible_branches(self):
        print("Possible")
        with open("test.xml", "wb") as f:
            f.write(etree.tostring(self.ra_pst_et))
        sum_poss_branches = len(self.ra_pst_et.xpath("//cpee1:children/cpee1:resource[count(ancestor::cpee1:children)=1]", namespaces=self.ns))
        max_len = 0
        branches_list = []
        ref_count = 0
        for task in self.task_list:
            possible_branches = task.xpath("cpee1:children/*", namespaces=self.ns)
            ref_count += len(possible_branches)
            branches_list.append(len(possible_branches))
            if len(possible_branches)> max_len:
                max_len = len(possible_branches)
            
        print("Correct?", ref_count == sum_poss_branches)
        print(branches_list)

        return np.zeros((len(self.task_list), max_len)), np.zeros(max_len)
    
    def get_possible_actions(self):
        sum_poss_branches = len(self.current_task.xpath("cpee1:children/cpee1:resource", namespaces=self.ns))
        
        return np.arange(sum_poss_branches)# list of len(#possible_branches)
    
    def sort_schedule_by_resource(self):
        self.schedule = dict(sorted(self.schedule.items())) 


    def calculate_makespan(self):
        # TODO:
        # calculate overall makespan
        max_task = 0
        for resource, tasks in self.schedule:
            res_max_task = self.schedule[resource][-1]["start"] + self.schedule[resource][-1]["duration"]
            if res_max_task > max_task: max_task = res_max_task 
        return max_task

    def print_schedule(self):
        # TODO:
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


#import tensorflow as tf
#from tensorflow.keras.models import Sequential
#from tensorflow.keras.layers import Dense
#from tensorflow.keras.optimizers import Adam

import random
from collections import deque

class DQNAgentConfiguration:
    def __init__(self, state_size, action_size):
        self.state_size = state_size # No_of_resources * 2 + (No_of_branches*No_of_resources) + No_of_branches
        # From Env all resources, current max job end time per resource, current resource workload
        # From Process: workload per resource per branch, Task Delta per Branch
        self.max_action_size = action_size # = max_branches_per_task
        # TODO: flattened matrix of valid branches per task (shape: no_of_tasks, max_branches_per_task)
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.max_action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state, possible_actions):
        if np.random.rand() <= self.epsilon:
            return random.choice(possible_actions)
        
        act_values = self.model.predict(state)
        mask = np.full(self.max_action_size, -np.inf)
        mask[possible_actions] = act_values[0, possible_actions]
        return np.argmax(mask)
    
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def load(self, name):
        self.model.load_weights(name)
    
    def save(self, name):
        self.model.save_weights(name)


