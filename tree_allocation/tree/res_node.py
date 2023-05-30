
import uuid
from .node import Node

class ResourceNode(Node):
    def __init__(self, resource_obj, name, resource_profile, task):
        super().__init__()
        self.resource_obj = resource_obj
        self.name = name
        self.resource_profile = resource_profile
        self.task = task
        self.node_type = "resource"
        if self.name == "nurse2":
            self.expected_time = 1
        else:
            self.expected_time = 2
    @property
    def get_name(self):
        return self.name