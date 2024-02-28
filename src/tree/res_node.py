
import uuid
from .node import Node
from lxml import etree


class ResourceNode(Node):
    def __init__(self,  name=None,resource_obj=None, resource_profile=None, task=None, measure={}, xml_str=None):
        super().__init__()
        self.resource_obj = resource_obj
        self.name = name
        self.resource_profile = resource_profile
        self.task = task
        self.node_type = "resource"

        self.resource_profiles:list(ResourceProfile) = []
        self.active_profile: ResourceProfile = None
        self.xml_str:str = xml_str
        self.measure = measure
    
    @classmethod
    def fromrawxml(cls, xml_str:str):
        task_xml = etree.fromstring(xml_str)
        return cls.frometree(task_xml)

    @classmethod
    def frometree(cls, xml_str:etree.Element):
        "Initialize TaskNode from raw xml_str which describes one task"
        res_xml = xml_str
        name = res_xml.attrib["name"]
        xml_str = xml_str
        instance = cls(name, xml_str=etree.tostring(xml_str))
        instance.create_profiles_from_xml()
        return instance
         
        
    @property
    def get_name(self):
        return self.name
    
    def add_resource_profile(self, profile_name:str, change_fragment:str, core_fragment:str, constraints:str, Direction:int): #TODO change to resource Profile only
        self.resource_profiles.append({"profile_name" : profile_name, "change_fragment" : change_fragment, "core_fragment" : core_fragment})
    
    def create_resource_profile(self, name:str, role:str, **kwargs): #TODO change to resource Profile only
        res_profile = ResourceProfile(name=name, role=role, resource=self, **kwargs)
        self.resource_profiles.append(res_profile)
        if len(self.resource_profiles) == 1:
            self.active_profile = self.resource_profiles[0]

    def create_profiles_from_xml(self):
        resource = etree.fromstring(self.xml_str)
        for resprofile in resource.xpath("resprofile"):
            attribs = resprofile.attrib
            change_patterns = resprofile.xpath("changepattern")
            measures = {str(measure.tag) : float(measure.text) for measure in resprofile.xpath("measures/*")}
            rp = ResourceProfile(attribs["id"], attribs["name"], attribs["role"], 
                                    self, change_patterns=change_patterns, task=attribs["task"], measure=measures)
            self.resource_profiles.append(rp)



class ResourceProfile(Node):
    def __init__(self, profile_id, name,  role, resource, change_patterns=[], task=str(), measure={}):
        super().__init__()
        self.profile_id:str = profile_id
        self.name:str = name
        self.role:str = role
        self.change_patterns:list = change_patterns
        self.task:str = task
        self.resource: ResourceNode = resource
        self.measure = measure
        print(f"RP {self.name} created with measures: {self.measure}")

    #TODO Create from xml-str.
    
    def info(self):
        return self.__dict__

    
if __name__ == "__main__":
    pass