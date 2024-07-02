from src.allocation.branch import Branch
from src.allocation.solution import Solution
from src.allocation.utils import get_next_task

from lxml import etree
import random
import copy
from collections import defaultdict
import numpy as np


class Reinforcement():
    def __init__(self, process_allocation, environment, agent):
        self.env = environment
        self.agent = agent


class JobShopEnv():
    def __init__(self, ra_pst, schedule=defaultdict(list)):
        self.ra_pst_xml = ra_pst
        self.ra_pst_et = etree.fromstring(ra_pst)
        # Holds information on existing schedule situation, all allocated tasks to machines
        self.schedule = schedule
        self.current_step = 0
        self.solution = Solution(self.ra_pst_et)
        self.final_config = None

        self.ns = {"cpee1": list(self.ra_pst_et.nsmap.values())[0], "ra_rpst": "http://cpee.org/ns/ra_rpst"}
        self.task_list = copy.deepcopy(self.ra_pst_et.xpath(
            "(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children)]", namespaces=self.ns))
        self.tasks_iter = copy.copy(iter(self.task_list))  # iterator

    def add_task_to_schedule(self, task):
        # TODO: Ensure precedence rules

        with open("task.xml", "wb") as f:
            f.write(etree.tostring(task))

        task = etree.fromstring(etree.tostring(task))
        resources = task.xpath(
            "cpee1:allocation/cpee1:resource", namespaces=self.ns)
        if resources:
            # TODO: make attribute independent
            resource, task_id, time, start_time = resources[0].attrib["id"], task.attrib["id"], float(task.xpath(
                "cpee1:allocation/cpee1:resource/cpee1:resprofile/cpee1:measures/cpee1:cost", namespaces=self.ns)[0].text), 0

            if self.schedule[resource]:
                start_time = self.schedule[resource][-1]["start"] + \
                    self.schedule[resource][-1]["duration"]

            self.schedule[resource].append(
                {"task": task_id, "duration": time, "start": start_time})
        else:
            raise ValueError(f"No resource found for task_id {task.attrib["id"]}")
        return self.schedule

    def reset(self):
        # TODO: reset state
        pass

    def get_state(self):
        # TODO:
        # returns the current state of the Environment
        # must probably return schedule & "unscheduled RA-PST"
        matrix = np.zeros((len(self.schedule.items()), 100000))
        # Transform Schedule to flat Array: 
        i = 0
        for key,value in self.schedule.items(): 
            for task in value:
                start = int(task["start"])
                duration = int(task["duration"])
                end = start + duration
                matrix[i][start:end] = 1
            i += 1

        return matrix.flatten()

    def step(self, action=None):
        # TODO:
        # Decides on Konfiguration and schedules it into Schedule
        # updates the State

        task = get_next_task(self.tasks_iter, self.solution)
        if task == "end":
            self.reload_etree()
            print("Etrees are the same: ", etree.tostring(
                self.final_config) == etree.tostring(self.ra_pst_et))
            if True:  # TODO: toggle if dynamic scheduling during config or after config is finished
                # TODO: create schedule for fully configured process
                to_schedule_list = copy.deepcopy(self.final_config.xpath(
                    "(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children or ancestor::cpee1:allocation)]", namespaces=self.ns))
                
                # TODO base scheduling on RA-PST Ancestors (if Ancestor parallel: schedule in parallel)
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
            current_task= task 
            branches = current_task.xpath(
                "cpee1:children/*", namespaces=self.ns)  # get branches of RA-PST
            with open("test.xml", "wb") as f:
                f.write(etree.tostring(current_task))

            
            #self.print_node_structure(current_task)
            
            et_elem = etree.Element(f"{{{self.ns["cpee1"]}}}children")
            et_elem.append(branches[random.randint(0, len(branches)-1)])

            # remove existing children to get branch
            for child in current_task.xpath("cpee1:children", namespaces=self.ns):
                current_task.remove(child)
            current_task.append(et_elem)
            branch = Branch(current_task)

            self.final_config = branch.apply_to_process(
                self.ra_pst_et, self.solution)
            with open("test.xml", "wb") as f:
                f.write(etree.tostring(self.final_config))
            # TODO: choose branch with reinforcement learn "action"
            # TODO: Get only the newly allocated tasks and schedule during Configuration
            #   ->  needed to get immidiate reward. Maybe Identification via label & resource
            # TODO: Set Reward based on Scheduling. Discounting for later decisions!
            #   ->  possibility to get reward + discounted reward?
            # TODO: Scheduling with good scheduler, Scheduling of one allocated task

            self.current_step += 1

        return None, None, None

    def calculate_makespan(self):
        # TODO:
        # calculate overall makespan
        pass

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


import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

import random
from collections import deque

class DQNAgentConfiguration:
    def __init__(self, state_size, action_size):
        self.state_size = state_size 
        # From Env all resources, all jobs per resource, current max makespan, current overall machine usage
        # From Process: Possible Configs Resources, exp. exec. times, earliest possible start time of task 
        self.action_size = action_size # could be len of process or just one int
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


