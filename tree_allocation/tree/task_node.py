import uuid, json
from .node import Node
from lxml import etree


class TaskNode(Node):

    def __init__(self, task_id:str=None, label:str=None, allowed_roles=[], task_tree:etree.Element=None, ns=None):
        super().__init__()
        self.task_id = task_id
        self.label = label
        self.allowed_roles = allowed_roles  
        self.node_type = "task"
        self.task_tree = task_tree
        self.ns = ns

    @classmethod
    def fromrawxml(cls, xml_str:str):
        "Initialize TaskNode from raw xml_str which describes one task"

        task_xml = etree.fromstring(xml_str)
        return cls.frometree(task_xml)
            
    @classmethod
    def frometree(cls, xml_str:etree.Element):
        "Initialize TaskNode from raw xml_str which describes one task"
        task_xml = xml_str
        ns = cls.parse_config()
        print(ns)

        if task_xml.tag == f"{{{ns['cpee1']}}}" + 'call':
            task_id  = task_xml.attrib["id"]
            label = task_xml.xpath("cpee1:parameters/cpee1:label", namespaces=ns)[0].text
            allowed_roles = task_xml.xpath("cpee1:resources/cpee1:resource", namespaces=ns)
            allowed_roles = [role.text for role in allowed_roles]
            task_xml = task_xml
            return cls(task_id, label, allowed_roles, task_xml, ns)
        
        elif task_xml.tag == f"{{{ns['cpee1']}}}" + 'manipulate':
            task_id  = task_xml.attrib["id"]
            label = task_xml.attrib["label"]
            allowed_roles = task_xml.xpath("cpee1:resources/cpee1:resource", namespaces=ns)
            allowed_roles = [role.text for role in allowed_roles]
            task_xml = task_xml
            return cls(task_id, label, allowed_roles, task_xml, ns)
        else:
            raise("XML-File does not represent a CPEE Task")
    

    @property
    def id(self):
        return self.task_id
    
    @property
    def get_name(self):
        return self.label