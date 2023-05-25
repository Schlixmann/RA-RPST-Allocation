import uuid
from .node import Node

class TaskNode(Node):
    def __init__(self, label, allowed_roles=[]):
        super().__init__()
        self.label = label
        self.allowed_roles = allowed_roles  

    @property
    def id(self):
        return self.__id
    
    @property
    def get_name(self):
        return self.label