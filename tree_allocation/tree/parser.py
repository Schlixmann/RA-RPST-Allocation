from lxml import etree
from .node import Node
from .gtw_node import GtwNode
from .task_node import TaskNode
from .res_node import ResourceNode

def parse_xml(process_xml, root=None):
    """
    Parses CPEE XML-Tree into an RDPM tree in python. 
    The Root node is a ProcessNode (just type node?)
    All its children are either task or Gateway nodes
    All tasks need Resource nodes as children
    
    """
    if not root:
        root = Node()

    
    for child in process_xml.xpath('child::*'):
        namespace = list(child.nsmap.values())[0]
        ns = {"ns": namespace}
        print("Child.tag: ", child.tag)
        print([f"{{{namespace}}}" + tag for tag in ["manipulate", "call"]])
        if str(child.tag) in  [f"{{{namespace}}}" + tag for tag in ["manipulate", "call"]]:
            attribs = dict(child.attrib)
            if child.tag == f"{{{namespace}}}" + "call":
                params = child.xpath("child::ns:parameters/ns:label", namespaces=ns)[0]

                attribs.update({'label' : params.text})
            new_child = TaskNode(attribs['id'], attribs['label'])
            root.add_child(new_child)
            parse_xml(child, new_child)

        elif str(child.tag) in  [f"{{{namespace}}}" + tag for tag in ["parallel", "choose", "loop"]]:
            gtw_type = child.tag.replace(str("{"+list(child.nsmap.values())[0]+"}"), "")
            new_child = GtwNode(gtw_type=gtw_type)
            root.add_child(new_child)
            parse_xml(child, new_child)
        
        else: 
            parse_xml(child, root)

        #print([child.tag for child in root.children])
    return root

if __name__ == "__main__":
    with open("main_process.xml") as f:
        process = etree.parse(f)
    
    parse_xml(process)

