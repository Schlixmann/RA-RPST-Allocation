import uuid
from .node import Node

class GtwNode(Node):
    def __init__(self, label=None, gtw_type="exclusive"):
        super().__init__()
        self.label = gtw_type
        self.gtw_type = gtw_type
        self.node_type = "gateway"