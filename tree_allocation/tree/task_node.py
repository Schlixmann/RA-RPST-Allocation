import uuid, json
from .node import Node
from lxml import etree


ns = {"cpee2": "http://cpee.org/ns/properties/2.0", 
        "cpee1":"http://cpee.org/ns/description/1.0"}


class TaskNode(Node):

    def __init__(self, task_id:str=None, label:str=None, allowed_roles=[], task_tree:etree.Element=None):
        super().__init__()
        self.task_id = task_id
        self.label = label
        self.allowed_roles = allowed_roles  
        self.node_type = "task"
        self.task_tree = task_tree

    @classmethod
    def fromrawxml(cls, xml_str:str):
        "Initialize TaskNode from raw xml_str which describes one task"
        task_xml = etree.fromstring(xml_str)

        if task_xml.tag == f"{{{cls.ns['cpee1']}}}" + 'call':
            task_id  = task_xml.attrib["id"]
            label = task_xml.xpath("cpee1:parameters/cpee1:label", namespaces=cls.ns)[0].text
            allowed_roles = task_xml.xpath("cpee1:resources/cpee1:resource", namespaces=cls.ns)
            allowed_roles = [role.text for role in allowed_roles]
            task_xml = task_xml
            return cls(task_id, label, allowed_roles, task_xml)
        
        elif task_xml.tag == f"{{{cls.ns['cpee1']}}}" + 'manipulate':
            task_id  = task_xml.attrib["id"]
            label = task_xml.attrib["label"]
            allowed_roles = task_xml.xpath("cpee1:resources/cpee1:resource", namespaces=cls.ns)
            allowed_roles = [role.text for role in allowed_roles]
            task_xml = task_xml
            return cls(task_id, label, allowed_roles, task_xml)
        else:
            raise("XML-File does not represent a CPEE Task")
            
    @classmethod
    def frometree(cls, xml_str:etree.Element):
        "Initialize TaskNode from raw xml_str which describes one task"
        task_xml = xml_str

        if task_xml.tag == f"{{{cls.ns['cpee1']}}}" + 'call':
            task_id  = task_xml.attrib["id"]
            label = task_xml.xpath("cpee1:parameters/cpee1:label", namespaces=cls.ns)[0].text
            allowed_roles = task_xml.xpath("cpee1:resources/cpee1:resource", namespaces=cls.ns)
            allowed_roles = [role.text for role in allowed_roles]
            task_xml = task_xml
            return cls(task_id, label, allowed_roles, task_xml)
        
        elif task_xml.tag == f"{{{cls.ns['cpee1']}}}" + 'manipulate':
            task_id  = task_xml.attrib["id"]
            label = task_xml.attrib["label"]
            allowed_roles = task_xml.xpath("cpee1:resources/cpee1:resource", namespaces=cls.ns)
            allowed_roles = [role.text for role in allowed_roles]
            task_xml = task_xml
            return cls(task_id, label, allowed_roles, task_xml)
        else:
            raise("XML-File does not represent a CPEE Task")
    

    @property
    def id(self):
        return self.task_id
    
    @property
    def get_name(self):
        return self.label