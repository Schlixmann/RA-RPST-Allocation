import unittest
from src.proc_resource import *
from src.helpers import *

class TestEvent(unittest.TestCase):
    def test_get_all_resourcees(self):
        resources =  get_all_resources("http://localhost:62000/resources")

        for res in resources:
            print(res.__dict__)
        


    def test_build_resourceProfile(self):
        res1 = Resource(name="Test_Resource")
        res1.create_resource_profile(name="test_profile", role="test_Role")
        print(res1.info())
        print(res1.resourceProfiles[0].info())