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

class CpeeParser():
    """ 
    Takes a Cpee Element and Parses it into RDPM Element 
    """

    def parse_loop(loop_xml:etree.Element, ns):
        out_xml = [loop_xml.remove(x) for x in loop_xml.xpath("*", namespaces=ns)]

        return loop_xml
    
    def parse_manipulate(man_xml:etree.Element, ns):
        for elem in man_xml.xpath("cpee1:resources/cpee1:resource", namespaces=ns):
            elem.tag = "allowed_role"
        return man_xml

    def parse_call(xml:etree.Element, ns):
        xml.attrib["label"] = xml.xpath("cpee1:parameters/cpee1:label", namespaces=ns)[0].text
        resources = xml.xpath("cpee1:resources", namespaces=ns)

        xml = [xml.remove(x) for x in xml.xpath("*", namespaces=ns)]
        xml.append(resources)
        for elem in xml.xpath("cpee1:resources/cpee1:resource", namespaces=ns):
            elem.tag = "allowed_role"

        return xml


def parse_factory(element_type = None, xml=None, ns=None):
    elem_factory= {
        f"{{{ns['cpee1']}}}loop" : CpeeParser.parse_loop,
        f"{{{ns['cpee1']}}}manipulate" : CpeeParser.parse_manipulate, 
        f"{{{ns['cpee1']}}}call" : CpeeParser.parse_call
    }
    print(elem_factory)
    return elem_factory[element_type](xml, ns)

def internal_process_parser(process_xml):
    root = etree.fromstring(process_xml)
    if len(root.xpath("*")) == 0:
        return root
    namespace = list(root.nsmap.values())[0]
    ns = {"cpee1": namespace}
    new_root = etree.Element(f"{{{ns['cpee1']}}}description")
    #input_process.xpath("//cpee1:description", namespaces = ns)[0]
    for elem in root.xpath("*"):
        try:
            new_root.append(parse_factory(str(elem.tag), elem, ns=ns))

        except:
            pass
    return new_root






if __name__ == "__main__":
    with open("main_process.xml") as f:
        process = etree.parse(f)
    
    parse_xml(process)

