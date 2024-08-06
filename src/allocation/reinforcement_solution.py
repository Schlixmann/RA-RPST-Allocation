from collections import deque
from src.allocation.branch import Branch
from src.allocation.solution import Solution
from src.allocation.utils import *

from lxml import etree
import random
import copy
from collections import defaultdict
import numpy as np

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam


class Reinforcement():
    def __init__(self, process_allocation, environment, agent):
        self.env = environment
        self.agent = agent


class JobShopEnv():
    def __init__(self, ra_pst, schedule=defaultdict(dict), current_instance_id=1):
        # self.ra_pst_xml = ra_pst
        self.ra_pst_et = ra_pst if isinstance(ra_pst, etree._Element) else etree.fromstring(ra_pst)
        
        self.ns = {"cpee1": list(self.ra_pst_et.nsmap.values())[
            0], "ra_rpst": "http://cpee.org/ns/ra_rpst"}
        self.task_list = copy.deepcopy(self.ra_pst_et.xpath(
            "(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children)]", namespaces=self.ns))
        self.tasks_iter = copy.copy(iter(self.task_list))  # iterator
        self.current_task_number = 0
        
        self.all_resources = set(self.ra_pst_et.xpath(
            "//cpee1:children/cpee1:resource/@id", namespaces=self.ns))
        
        # Holds information on existing schedule situation, all allocated tasks to machines
        self.schedule = schedule if schedule else self.create_random_schedule()

        self.init_ra_pst_et = copy.deepcopy(self.ra_pst_et)
        self.current_ = 0
        self.final_config = copy.deepcopy(self.ra_pst_et)
        self.solution = Solution(self.final_config)
        self.to_delete = []
        self.valid_solution = []
        self.current_instance_id = current_instance_id
        self.actions = []
        
        self.init_last_task = self.get_last_scheduled_task_end()
        self.last_task_end = 0
        self.previous_task = None

    def get_next_schedule_id(self):
        highest_id = 0
        for resource, tasks in self.schedule.items():
            for task, values in tasks.items():
                highest_id = max(highest_id, values['id'])
        return highest_id + 1
    
    def create_random_schedule(self, max_schedule_length = 400, no_of_blocks_range = (1,50), times_range = (10, 150)):
        schedule = defaultdict(dict)
        a,b = no_of_blocks_range
        no_of_blocks = random.randint(a,b)
        
        print(f"Create random Schedule with {no_of_blocks} and max length {max_schedule_length}")
        for i in range(no_of_blocks):
            resource = list(self.all_resources)[random.randint(0, len(list(self.all_resources))-1)]
            task_id = 'fix_' + str(i)
            start, end = times_range
            duration = random.randint(start, end)
            schedule[resource][task_id] = ({"task": task_id, 'instance_id' : 'fix', 'id': i, "start": random.randrange(0, max_schedule_length-duration, 10), "duration": duration})
        
        return schedule
    
    def get_last_scheduled_task_end(self):
        self.sort_schedule_by_resource()
        max_last_task = 0
        last_tasks = defaultdict(dict)
        for resource, tasks in self.schedule.items():
            last_task = {"start": 0, "duration": 0}
            for task, values in tasks.items():
                if values["start"] + values["duration"] >= last_task["start"] + last_task["duration"]:
                    last_task = values

            last_task_end = last_task["start"] + last_task["duration"]
            if last_task_end > max_last_task:
                max_last_task, self.last_task_end = last_task_end, last_task_end
        return self.last_task_end

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
        resources = proc_task.xpath(
            "cpee1:allocation/cpee1:resource", namespaces=self.ns)
        if resources:
            # TODO: make attribute independent
            # TODO: set start time on previous task in process
            resource, instance_id, task_id, time = resources[0].attrib["id"], self.current_instance_id, proc_task.attrib["id"], float(proc_task.xpath(
                "cpee1:allocation/cpee1:resource/cpee1:resprofile/cpee1:measures/cpee1:cost", namespaces=self.ns)[0].text)

            # find earliest_possible_start_time
            if previous_task:
                earliest_possible_start_time = previous_task["start"] + \
                    previous_task["duration"]
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
                            earliest_possible_start_time = values["start"] + \
                                values["duration"]
                            earliest_possible_end_time = earliest_possible_start_time + time
                            continue
                        elif earliest_possible_start_time > values["start"] and earliest_possible_start_time < values["start"] + values["duration"]:
                            conflict = True
                            earliest_possible_start_time = values["start"] + \
                                values["duration"]
                            earliest_possible_end_time = earliest_possible_start_time + time
                            continue
                        else:
                            conflict = False

            task_in_config = self.solution.solution_ra_pst.xpath(
                f"//*[@id = '{proc_task.attrib['id']}']")[0]
            schedule_id = self.get_next_schedule_id()
            task_in_config.attrib["schedule_id"] = str(schedule_id)

            self.schedule[resource][f"{task_id}_{instance_id}"] = {"task": task_id,
                                                                   "instance_id": instance_id, 
                                                                   "id": schedule_id, 
                                                                   "duration": time, 
                                                                   "start": earliest_possible_start_time}

        else:
            pass
            # raise ValueError(f"No resource found for task_id {task.attrib["id"]}")
        return self.schedule

    def reset(self):
        # TODO: reset state
        

        self.schedule = self.create_random_schedule()
        self.current_task_number = -1
        self.ra_pst_et = copy.deepcopy(self.init_ra_pst_et)

        self.task_list = copy.deepcopy(self.ra_pst_et.xpath(
            "(//cpee1:call|//cpee1:manipulate)[not(ancestor::cpee1:children)]", namespaces=self.ns))
        self.tasks_iter = copy.copy(iter(self.task_list))  # iterator

        self.current_task_number = 0
        self.final_config = copy.deepcopy(self.ra_pst_et)
        self.solution = Solution(self.final_config)
        self.to_delete = []
        self.valid_solution = []
        self.actions = []
        self.init_last_task = self.get_last_scheduled_task_end()

        return self.get_state_aggregation()

    def get_schedule_state(self):
        # TODO:
        # returns the current state of the Environment
        # must probably return schedule & "unscheduled RA-PST"
        matrix = np.zeros((len(self.all_resources), 100000))
        # Transform Schedule to flat Array:
        for resource, tasks in self.schedule.items():
            for task_id, values in tasks.items():
                start = int(values["start"])
                duration = int(values["duration"])
                end = start + duration
                matrix[list(self.all_resources).index(resource)][start:end] = 1

        return matrix.flatten()

    def get_state_aggregation(self):
        # Resource Coverage
        # Endtime of last Scheduled item per Resource
        # Resource Coverage per Resource per available branch
        # Task Delta per branch
        # TODO: Get earliest possible start time for next task
        self.sort_schedule_by_resource()
        max_last_task = 0
        last_tasks = defaultdict(dict)
        for resource, tasks in self.schedule.items():
            last_task = {"start": 0, "duration": 0}
            for task, values in tasks.items():
                if values["start"] + values["duration"] >= last_task["start"] + last_task["duration"]:
                    last_task = values

            last_task_end = last_task["start"] + last_task["duration"]
            if last_task_end > max_last_task:
                max_last_task, self.last_task_end = last_task_end, last_task_end

            last_tasks[resource]["last_task"] = last_task

        #TODO: 
        # give reward to deletes
        # branch costs per resource in [max(branchlength),resources]
        arr, max_branch_no = self.get_possible_branches()
        branch_costs = np.zeros((len(max_branch_no), len(self.all_resources)+1))
        
        if self.solution.current_task != 'end':
            i = 0 
            for branch in self.solution.get_branches_for_task_wrap(self.solution.current_task):
                j=0
                for resource_id in self.all_resources:
                    costs = sum([float(cost) for cost in branch.node.xpath(f".//cpee1:resource[@id ='{resource_id}']/cpee1:resprofile/cpee1:measures/cpee1:cost/text()", namespaces=self.solution.ns)])
                    branch_costs[i,j] = costs
                    j+=1
                
                if branch.node.xpath(f".//cpee1:changepattern[@type = 'delete']", namespaces=self.solution.ns):
                    # Add 1 in last row of matrix, if branch deletes a task
                    branch_costs[i, -1] = 1
                i+=1 

        fin_list = np.zeros((2, len(self.all_resources)))
        for resource, values in last_tasks.items():
            last_tasks[resource]["attributes"] = {"coverage": sum(
                values["duration"] for task, values in self.schedule[resource].items()) / max_last_task}
            fin_list[0][int(str(resource)[-1]) -
                        1] = (last_tasks[resource]["attributes"]["coverage"])
            fin_list[1][int(str(resource)[-1])-1] = float((last_tasks[resource]
                                                           ["last_task"]["start"]+last_tasks[resource]["last_task"]["duration"]))

        # determine earliest possible starting time for next task: 
        task_in_sched = None
        if self.previous_task:
            task_in_sched = self.previous_task.attrib["id"] + f"_{self.current_instance_id}"
        
        earliest_start = 0
        for resource in self.schedule.values():
            for key, values in resource.items():
                if key == task_in_sched:
                    earliest_start = values["start"] + values["duration"]
                    break

        flat_schedule = self.get_schedule_state()
        state = np.concatenate((flat_schedule, fin_list.flatten(), branch_costs.flatten(), np.array([self.current_task_number]), np.array([earliest_start])))
        self.current_task_number += 1
        return state

    def step(self, action=None):

        # TODO:
        # Decides on Konfiguration and schedules it into Schedule
        # updates the State
        self.actions.append(action)
        task = self.solution.current_task

        # for now, choose random branch
        possible_branches = self.solution.get_branches_for_task_wrap(task)

        # TODO: Choose branch based on action
        #   Reward: direct impact + notion on overall validity
        #   Reward: direct impact must come from scheduling
        #   Reward: discount later schedulings

        # self.print_node_structure(current_task)

        print("Action: ", action, "Current_task: ", task.attrib["id"])
        #et_elem = etree.Element(f"{{{self.ns["cpee1"]}}}children")
        if not action:
            action = random.randint(0, len(possible_branches)-1)

        self.previous_task = self.solution.current_task
        self.solution.apply_branches([action])

        self.valid_solution.append(self.solution.invalid_branches)
        branch = self.solution.get_branches_for_task_wrap(task)[action]

        for task in branch.node.xpath("(//cpee1:manipulate|//cpee1:call)[not(ancestor::cpee1:changepattern)]", namespaces=self.ns):
            # find task in final konfig:
            # label = task.attrib["label"]
            with open("text.xml", "wb") as f:
                f.write(etree.tostring(branch.node))

            self.reload_etree()
            label = get_label(etree.tostring(task))
            if ("type", "delete") in task.attrib.items():
                # deleted task must not be scheduled
                continue

            proc_task = self.solution.solution_ra_pst.xpath(f"(//cpee1:manipulate[@label='{label}']|//cpee1:call/cpee1:parameters/cpee1:label[text()='{label}']/ancestor::*[2])[not(ancestor::cpee1:children|ancestor::cpee1:allocation)]", namespaces=self.ns)
            if len(proc_task) > 1:
                raise ValueError

            self.add_task_to_schedule(proc_task[0], label)
            # Maybe give last scheduled task here

        # TODO: Set Reward based on Scheduling. Discounting for later decisions!
        #   ->  possibility to get reward + discounted reward?
        # TODO: Scheduling with good scheduler, Scheduling of one allocated task

        if self.solution.current_task == "end":
            self.reload_etree()
            #print("Etrees are the same: ", etree.tostring(
            #    self.solution.solution_ra_pst) == etree.tostring(self.ra_pst_et))

            # TODO: Fix all namespace issues
            #self.solution.process = etree.fromstring(
            #    etree.tostring(self.solution.process))
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
        #with open("test.xml", "wb") as f:
        #    f.write(etree.tostring(self.ra_pst_et))
        branches_list = self.solution.get_possible_branches()
        sum_poss_branches = sum(np.asarray(branches_list)+1)
        max_len = 0
        ref_count = 0
        for task in self.task_list:
            possible_branches = self.solution.get_branches_for_task_wrap(task)
            ref_count += len(possible_branches)
            if len(possible_branches) > max_len:
                max_len = len(possible_branches)

        print("Correct?", ref_count == sum_poss_branches)
        print(branches_list)

        return np.zeros((len(self.task_list), max_len)), np.zeros(max_len)

    def get_possible_actions(self):
        sum_poss_branches = len(self.solution.current_task.xpath(
            "cpee1:children/cpee1:resource", namespaces=self.ns))

        return np.arange(sum_poss_branches)  # list of len(#possible_branches)

    def sort_schedule_by_resource(self):
        self.schedule = defaultdict(dict, sorted(self.schedule.items()))

    def calculate_makespan(self):
        # TODO:
        # calculate overall makespan
        max_task = 0
        for resource, tasks in self.schedule:
            res_max_task = self.schedule[resource][-1]["start"] + \
                self.schedule[resource][-1]["duration"]
            if res_max_task > max_task:
                max_task = res_max_task
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
        self.solution.solution_ra_pst = etree.fromstring(
            etree.tostring(self.solution.solution_ra_pst))

class DQNAgentConfiguration:
    def __init__(self, state_size, action_size):
        # No_of_resources * 2 + (No_of_branches*No_of_resources) + No_of_branches
        self.state_size = state_size
        # From Env all resources, current max job end time per resource, current resource workload
        # From Process: workload per resource per branch, Task Delta per Branch
        self.max_action_size = action_size  # = max_branches_per_task
        # TODO: flattened matrix of valid branches per task (shape: no_of_tasks, max_branches_per_task)
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.randomness_counter = 0

    def _build_model(self):
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.max_action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(
            learning_rate=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        print("Start remember: ")
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, possible_actions):
        if np.random.rand() <= self.epsilon:
            self.randomness_counter += 1
            return random.choice(possible_actions)

        act_values = self.model.predict(state)
        mask = np.full(self.max_action_size, -np.inf)
        mask[possible_actions] = act_values[0, possible_actions]
        return np.argmax(mask)

    def replay(self, batch_size):
        print("Start Replay:")
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

    def save_model(self, model_path, epsilon_path):
        self.model.save(model_path)
        with open(epsilon_path, 'w') as f:
            f.write(str(self.epsilon))

    def load_model(self, model_path, epsilon_path):
        self.model = load_model(model_path)
        with open(epsilon_path, 'r') as f:
            self.epsilon = float(f.read())
