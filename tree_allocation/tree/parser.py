from lxml import etree
from .node import Node
from .gtw_node import GtwNode
from .task_node import TaskNode
from .res_node import ResourceNode

def parse_xml(process_xml, tree_node=None):
    """
    Parses CPEE XML-Tree into an RDPM tree in python. 
    The Root node is a ProcessNode (just type node?)
    All its children are either task or Gateway nodes
    All tasks need Resource nodes as children
    
    """
    if not tree_node:
        root = Node()
    
    for child in process_xml.xpath('child::*'):
        namespace = list(child.nsmap.values())[0]
        print(namespace)
        if child.tag in  [namespace + tag for tag in ["manipulate", "call"]]:
            attribs = child.attrib
            new_child = TaskNode(attribs['id'], attribs['label'])
            root.add_child(new_child)
        else:
            type = child.tag.replace(str("{"+list(child.nsmap.values())[0]+"}"), "")
            new_child = GtwNode("parallel")
        print(root.children)


if __name__ == "__main__":
    with open("main_process.xml") as f:
        process = etree.parse(f)
    
    parse_xml(process)

