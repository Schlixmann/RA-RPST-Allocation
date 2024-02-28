import unittest
from src.proc_resource import *

class TestEvent(unittest.TestCase):
    def test_build_resource(self):
        res1 = Resource(name="Test_Resource")

        print(res1.info())


    def test_build_resourceProfile(self):
        res1 = Resource(name="Test_Resource")
        res1.create_resource_profile(name="test_profile", role="test_Role")
        print(res1.info())
        print(res1.resourceProfiles[0].info())