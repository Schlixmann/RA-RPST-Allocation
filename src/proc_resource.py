# TODO
# Add Resources in this File
import random

class Resource():
    def __init__(self, name):
        self.name: str = name
        self.resource_profiles:list(ResourceProfile) = []
        self.active_profile: ResourceProfile = None

    def info(self):
        return self.__dict__
    
    def get_profile_list(self):
        return self.resource_profiles

    def add_resource_profile(self, profile_name:str, change_fragment:str, core_fragment:str, constraints:str, Direction:int): #TODO change to resource Profile only
        self.resource_profiles.append({"profile_name" : profile_name, "change_fragment" : change_fragment, "core_fragment" : core_fragment})
    
    def create_resource_profile(self, name:str, role:str, **kwargs): #TODO change to resource Profile only
        res_profile = ResourceProfile(name=name, role=role, resource=self, **kwargs)
        self.resource_profiles.append(res_profile)
        if len(self.resource_profiles) == 1:
            self.active_profile = self.resource_profiles[0]

    
    

class ResourceProfile():
    def __init__(self, name,  role, resource, change_patterns=[], task=str(), measure={}):
        self.name:str = name
        self.role:str = role
        self.change_patterns:list() = change_patterns
        self.task:str() = task
        self.resource: Resource = resource
        self.measure = measure
        print(f"RP {self.name} created with measures: {self.measure}")
    
    def info(self):
        return self.__dict__
    
if __name__ == "__main__":
    pass
